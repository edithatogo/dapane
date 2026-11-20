use crate::{
    ContractError, EventRef, Extent, Instant, ObjectLink, ObjectRef, ObjectRelation,
    ObservationWindow, Snapshot, SourceFormat, SourceIdentity, UseAssertion, ValidatedContract,
    instant, token, validate_contract,
};
use roxmltree::{Document, Node, ParsingOptions};
use serde::{
    Deserialize, Deserializer,
    de::{MapAccess, Visitor, value::MapAccessDeserializer},
};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::{
    collections::{BTreeMap, BTreeSet},
    fmt,
    marker::PhantomData,
};
use time::{OffsetDateTime, format_description::well_known::Rfc3339};

/// Maximum uncompressed UTF-8 bytes admitted by either native adapter.
pub const MAX_NATIVE_BYTES: usize = 8 * 1024 * 1024;
const XES_NS: &str = "http://www.xes-standard.org/";

/// Source identity, observation coverage and explicitly mapped usage.
pub struct ObservationInput {
    /// Stable source namespace.
    pub namespace: String,
    /// Immutable source revision.
    pub revision: String,
    /// Observation coverage chosen by the caller.
    pub window: ObservationWindow,
    /// Caller supplied resource quantities and event anchors.
    pub uses: Vec<UseAssertion>,
}

/// Required source mapping for a trace-centric XES file.
pub struct XesObjectContext {
    /// Stable object identities from an explicit external mapping.
    pub objects: Vec<ObjectRef>,
    /// Explicit qualified links keyed by native XES event IDs.
    pub event_objects: BTreeMap<String, Vec<ObjectLink>>,
    /// Explicit object-to-object relationships.
    pub relations: Vec<ObjectRelation>,
}

/// An import failure before a costing projection is available.
#[derive(Debug)]
pub enum ImportError {
    /// Unsupported source shape, identity, association or timestamp.
    Format(&'static str),
    /// Invalid projected observation contract.
    Contract(ContractError),
}

impl fmt::Display for ImportError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Format(message) => formatter.write_str(message),
            Self::Contract(error) => error.fmt(formatter),
        }
    }
}
impl std::error::Error for ImportError {}
impl From<ContractError> for ImportError {
    fn from(error: ContractError) -> Self {
        Self::Contract(error)
    }
}

/// Validated projection bound to the exact original native source bytes.
#[derive(Debug)]
pub struct NativeObservation<'a> {
    raw: &'a [u8],
    contract: ValidatedContract,
}

impl<'a> NativeObservation<'a> {
    /// Access the full retained native log without reserializing it.
    pub fn source_bytes(&self) -> &'a [u8] {
        self.raw
    }

    /// Access its validated costing projection.
    pub fn contract(&self) -> &ValidatedContract {
        &self.contract
    }
}

fn utf8(raw: &[u8]) -> Result<&str, ImportError> {
    if raw.is_empty() || raw.len() > MAX_NATIVE_BYTES {
        return Err(ImportError::Format(
            "native file exceeds the supported byte bounds",
        ));
    }
    std::str::from_utf8(raw).map_err(|_| ImportError::Format("native file must be UTF-8"))
}

fn timestamp(value: &str) -> Result<Instant, ImportError> {
    let invalid = ImportError::Format("expected a bounded RFC 3339 timestamp with explicit offset");
    if value.get(17..19) == Some("60")
        || value.ends_with("-00:00")
        || value.split_once('.').is_some_and(|(_, fraction)| {
            fraction.bytes().take_while(u8::is_ascii_digit).count() > 9
        })
    {
        return Err(invalid);
    }
    let parsed = OffsetDateTime::parse(value, &Rfc3339).map_err(|_| invalid)?;
    let result = Instant {
        unix_seconds: parsed.unix_timestamp(),
        nanosecond: parsed.nanosecond(),
    };
    instant(result, "/native/time")?;
    Ok(result)
}

fn finalize(
    raw: &[u8],
    input: ObservationInput,
    format: SourceFormat,
    objects: Vec<ObjectRef>,
    events: Vec<EventRef>,
    relations: Vec<ObjectRelation>,
) -> Result<NativeObservation<'_>, ImportError> {
    let contract = validate_contract(Snapshot {
        source: SourceIdentity {
            namespace: input.namespace,
            revision: input.revision,
            format,
            content_digest: format!(
                "sha256:{}",
                Sha256::digest(raw)
                    .iter()
                    .map(|byte| format!("{byte:02x}"))
                    .collect::<String>()
            ),
        },
        window: input.window,
        uses: input.uses,
        objects,
        events,
        relations,
    })?;
    Ok(NativeObservation { raw, contract })
}

struct JsonObject<T>(T);

struct ObjectVisitor<T>(PhantomData<T>);

impl<'de, T: Deserialize<'de>> Visitor<'de> for ObjectVisitor<T> {
    type Value = JsonObject<T>;

    fn expecting(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str("a JSON object")
    }

    fn visit_map<M: MapAccess<'de>>(self, map: M) -> Result<Self::Value, M::Error> {
        T::deserialize(MapAccessDeserializer::new(map)).map(JsonObject)
    }
}

impl<'de, T: Deserialize<'de>> Deserialize<'de> for JsonObject<T> {
    fn deserialize<D: Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        deserializer.deserialize_map(ObjectVisitor(PhantomData))
    }
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields, rename_all = "camelCase")]
struct Ocel {
    event_types: Vec<JsonObject<TypeDefinition>>,
    object_types: Vec<JsonObject<TypeDefinition>>,
    events: Vec<JsonObject<OcelEvent>>,
    objects: Vec<JsonObject<OcelObject>>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct TypeDefinition {
    name: String,
    attributes: Vec<JsonObject<AttributeDefinition>>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct AttributeDefinition {
    name: String,
    #[serde(rename = "type")]
    kind: AttributeKind,
}

#[derive(Clone, Copy, Deserialize)]
#[serde(rename_all = "lowercase")]
enum AttributeKind {
    String,
    Time,
    Integer,
    Float,
    Boolean,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct OcelEvent {
    id: String,
    #[serde(rename = "type")]
    kind: String,
    time: String,
    #[serde(default)]
    attributes: Vec<JsonObject<EventAttribute>>,
    #[serde(default)]
    relationships: Vec<JsonObject<Link>>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct OcelObject {
    id: String,
    #[serde(rename = "type")]
    kind: String,
    #[serde(default)]
    attributes: Vec<JsonObject<ObjectAttribute>>,
    #[serde(default)]
    relationships: Vec<JsonObject<Link>>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct EventAttribute {
    name: String,
    value: Value,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct ObjectAttribute {
    name: String,
    time: String,
    value: Value,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields, rename_all = "camelCase")]
struct Link {
    object_id: String,
    qualifier: String,
}

type Attributes = BTreeMap<String, AttributeKind>;
type Definitions = BTreeMap<String, Attributes>;

fn definitions(types: Vec<JsonObject<TypeDefinition>>) -> Result<Definitions, ImportError> {
    let mut result = BTreeMap::new();
    for JsonObject(definition) in types {
        token(&definition.name, "/native/type/name", false)?;
        let mut fields = BTreeMap::new();
        for JsonObject(field) in definition.attributes {
            token(&field.name, "/native/type/attribute", false)?;
            if fields.insert(field.name, field.kind).is_some() {
                return Err(ImportError::Format("duplicate OCEL attribute declaration"));
            }
        }
        if result.insert(definition.name, fields).is_some() {
            return Err(ImportError::Format("duplicate OCEL type declaration"));
        }
    }
    Ok(result)
}

fn attributes<'a>(definitions: &'a Definitions, kind: &str) -> Result<&'a Attributes, ImportError> {
    definitions
        .get(kind)
        .ok_or(ImportError::Format("undeclared OCEL type"))
}

fn attribute_value(fields: &Attributes, name: &str, value: &Value) -> Result<(), ImportError> {
    let valid = match fields.get(name) {
        Some(AttributeKind::String) => value.is_string(),
        Some(AttributeKind::Time) => value.as_str().is_some_and(|text| timestamp(text).is_ok()),
        Some(AttributeKind::Integer) => value.is_i64(),
        Some(AttributeKind::Float) => value.is_number(),
        Some(AttributeKind::Boolean) => value.is_boolean(),
        None => false,
    };
    if !valid {
        return Err(ImportError::Format(
            "OCEL attribute differs from its declared scalar type",
        ));
    }
    Ok(())
}

/// Import bounded OCEL 2.0 JSON, including qualified event/object associations.
///
/// The checked profile uses explicit offsets, declared scalar attributes and
/// signed 64-bit integers. Original attributes and history remain in the bytes.
pub fn import_ocel2(
    raw: &[u8],
    input: ObservationInput,
) -> Result<NativeObservation<'_>, ImportError> {
    let JsonObject(source): JsonObject<Ocel> = serde_json::from_str(utf8(raw)?)
        .map_err(|_| ImportError::Format("invalid bounded OCEL 2.0 JSON"))?;
    let event_definitions = definitions(source.event_types)?;
    let object_definitions = definitions(source.object_types)?;
    let mut objects = Vec::new();
    let mut relations = Vec::new();
    for JsonObject(object) in source.objects {
        let fields = attributes(&object_definitions, &object.kind)?;
        let mut seen = BTreeSet::new();
        for JsonObject(value) in object.attributes {
            attribute_value(fields, &value.name, &value.value)?;
            if !seen.insert((value.name, timestamp(&value.time)?)) {
                return Err(ImportError::Format(
                    "duplicate OCEL object attribute instant",
                ));
            }
        }
        for JsonObject(link) in object.relationships {
            relations.push(ObjectRelation {
                from: object.id.clone(),
                to: link.object_id,
                qualifier: link.qualifier,
            });
        }
        objects.push(ObjectRef {
            id: object.id,
            kind: object.kind,
        });
    }
    let mut events = Vec::new();
    for JsonObject(event) in source.events {
        let fields = attributes(&event_definitions, &event.kind)?;
        let mut seen = BTreeSet::new();
        for JsonObject(value) in event.attributes {
            attribute_value(fields, &value.name, &value.value)?;
            if !seen.insert(value.name) {
                return Err(ImportError::Format("duplicate OCEL event attribute"));
            }
        }
        events.push(EventRef {
            id: event.id,
            at: Some(timestamp(&event.time)?),
            objects: event
                .relationships
                .into_iter()
                .map(|JsonObject(link)| ObjectLink {
                    object_id: link.object_id,
                    qualifier: link.qualifier,
                })
                .collect(),
        });
    }
    finalize(
        raw,
        input,
        SourceFormat::Ocel2Json,
        objects,
        events,
        relations,
    )
}

fn xes_attributes<'a>(
    node: Node<'a, '_>,
    structural: &[&str],
) -> Result<BTreeMap<&'a str, (&'a str, &'a str)>, ImportError> {
    let mut result = BTreeMap::new();
    for child in node.children().filter(Node::is_element) {
        let tag = child.tag_name();
        if tag.namespace() != Some(XES_NS) {
            return Err(ImportError::Format("invalid XES element namespace"));
        }
        if structural.contains(&tag.name()) {
            continue;
        }
        let (Some(key), Some(value)) = (child.attribute("key"), child.attribute("value")) else {
            return Err(ImportError::Format("expected a scalar XES key and value"));
        };
        if !matches!(
            tag.name(),
            "string" | "id" | "date" | "int" | "float" | "boolean"
        ) || child.children().any(|node| node.is_element())
            || result.insert(key, (tag.name(), value)).is_some()
        {
            return Err(ImportError::Format(
                "unsupported or duplicate XES attribute",
            ));
        }
    }
    Ok(result)
}

fn xes_field<'a>(
    fields: &BTreeMap<&'a str, (&'a str, &'a str)>,
    key: &str,
    tag: &str,
) -> Result<&'a str, ImportError> {
    fields
        .get(key)
        .filter(|(kind, _)| *kind == tag)
        .map(|(_, value)| *value)
        .ok_or(ImportError::Format(
            "missing or mistyped required XES attribute",
        ))
}

/// Import XES 2.0 UTF-8 with explicit trace and event IDs and times.
///
/// The caller supplies the object graph. An interval's present anchors must
/// name the appropriate start/complete transitions of one activity and trace.
pub fn import_xes<'a>(
    raw: &'a [u8],
    input: ObservationInput,
    mut context: XesObjectContext,
) -> Result<NativeObservation<'a>, ImportError> {
    let text = utf8(raw)?;
    if text.contains("<!DOCTYPE") {
        return Err(ImportError::Format(
            "XES permits no document-type declaration",
        ));
    }
    let options = ParsingOptions {
        nodes_limit: 200_000,
        ..ParsingOptions::default()
    };
    let document = Document::parse_with_options(text, options)
        .map_err(|_| ImportError::Format("invalid bounded XES XML"))?;
    let log = document.root_element();
    if !log.has_tag_name((XES_NS, "log")) || log.attribute("xes.version") != Some("2.0") {
        return Err(ImportError::Format("expected an XES 2.0 log"));
    }
    xes_attributes(log, &["trace", "extension", "classifier", "global"])?;
    let mut trace_ids = BTreeSet::new();
    let mut anchors = BTreeMap::new();
    let mut events = Vec::new();
    for trace in log
        .children()
        .filter(|node| node.has_tag_name((XES_NS, "trace")))
    {
        let fields = xes_attributes(trace, &["event"])?;
        let trace_id = xes_field(&fields, "identity:id", "id")?;
        token(trace_id, "/native/trace/id", false)?;
        if !trace_ids.insert(trace_id) {
            return Err(ImportError::Format("duplicate XES trace identity"));
        }
        for event in trace
            .children()
            .filter(|node| node.has_tag_name((XES_NS, "event")))
        {
            let fields = xes_attributes(event, &[])?;
            let id = xes_field(&fields, "identity:id", "id")?;
            let activity = xes_field(&fields, "concept:name", "string")?;
            let transition = xes_field(&fields, "lifecycle:transition", "string")?;
            if anchors
                .insert(id, (trace_id, activity, transition))
                .is_some()
            {
                return Err(ImportError::Format("duplicate XES event identity"));
            }
            events.push(EventRef {
                id: id.into(),
                at: Some(timestamp(xes_field(&fields, "time:timestamp", "date")?)?),
                objects: context
                    .event_objects
                    .remove(id)
                    .ok_or(ImportError::Format("missing XES event object mapping"))?,
            });
        }
    }
    if !context.event_objects.is_empty() {
        return Err(ImportError::Format(
            "XES context references an absent event",
        ));
    }
    for assertion in &input.uses {
        let Extent::Interval {
            start_event_id,
            end_event_id,
            ..
        } = &assertion.extent
        else {
            continue;
        };
        let anchor = |id: &str, transition| {
            anchors
                .get(id)
                .filter(|(_, _, kind)| *kind == transition)
                .map(|(trace, activity, _)| (*trace, *activity))
                .ok_or(ImportError::Format("inconsistent XES lifecycle anchor"))
        };
        let start = start_event_id
            .as_deref()
            .map(|id| anchor(id, "start"))
            .transpose()?;
        let end = end_event_id
            .as_deref()
            .map(|id| anchor(id, "complete"))
            .transpose()?;
        if start.zip(end).is_some_and(|(start, end)| start != end) {
            return Err(ImportError::Format(
                "XES interval crosses traces or activities",
            ));
        }
    }
    finalize(
        raw,
        input,
        SourceFormat::Xes,
        context.objects,
        events,
        context.relations,
    )
}
