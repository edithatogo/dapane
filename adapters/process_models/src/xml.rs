//! Strict bounded XML subset parser with zero external XML dependencies.
//!
//! Explicitly rejects DOCTYPE declarations, external entities, internal entity
//! declarations, NOTATION declarations, CDATA sections, and non-`<?xml`
//! processing instructions so XML inputs fail closed.

use std::collections::BTreeMap;

use crate::model::{ErrorCode, ModelError};

/// Maximum XML document byte length accepted by the parser.
pub const MAX_XML_BYTES: usize = 262_144;
/// Maximum XML element nesting depth accepted by the parser.
pub const MAX_XML_DEPTH: usize = 32;
/// Maximum total XML elements accepted in one document.
pub const MAX_XML_ELEMENTS: usize = 4_096;
/// Maximum attributes permitted on a single XML element.
pub const MAX_XML_ATTRIBUTES: usize = 64;

/// Parsed XML element node with resolved namespace binding.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct XmlNode {
    /// Resolved namespace URI, if any.
    pub namespace: Option<String>,
    /// Local element name without namespace prefix.
    pub local_name: String,
    /// Original prefixed or unprefixed tag name.
    pub raw_name: String,
    /// Element attributes keyed by original attribute name (excluding `xmlns*`).
    pub attributes: BTreeMap<String, String>,
    /// Direct child elements in document order.
    pub children: Vec<XmlNode>,
    /// Normalized direct text content attached to this element.
    pub text: String,
}

impl XmlNode {
    /// Return trimmed text content for this node.
    pub fn trimmed_text(&self) -> &str {
        self.text.trim()
    }

    /// Return the first direct child matching `(namespace, local_name)`.
    pub fn child(&self, namespace: &str, local_name: &str) -> Option<&XmlNode> {
        self.children
            .iter()
            .find(|c| c.namespace.as_deref() == Some(namespace) && c.local_name == local_name)
    }
}

struct Parser<'a> {
    bytes: &'a [u8],
    src: &'a str,
    pos: usize,
    elements: usize,
}

type NsScope = BTreeMap<String, String>;

impl<'a> Parser<'a> {
    fn new(src: &'a str) -> Self {
        Self {
            bytes: src.as_bytes(),
            src,
            pos: 0,
            elements: 0,
        }
    }

    fn err(&self, code: ErrorCode, path: &str, message: impl Into<String>) -> ModelError {
        ModelError::new(code, path, message)
    }

    fn rest(&self) -> &'a str {
        &self.src[self.pos..]
    }

    fn starts_with(&self, pat: &str) -> bool {
        self.rest().starts_with(pat)
    }

    fn skip_ws(&mut self) {
        while let Some(b) = self.bytes.get(self.pos) {
            if matches!(b, b' ' | b'\t' | b'\r' | b'\n') {
                self.pos += 1;
            } else {
                break;
            }
        }
    }

    fn skip_comment(&mut self, path: &str) -> Result<(), ModelError> {
        self.pos += 4;
        let Some(end) = self.rest().find("-->") else {
            return Err(self.err(ErrorCode::MalformedXml, path, "Unterminated XML comment"));
        };
        let body = &self.rest()[..end];
        if body.contains("--") {
            return Err(self.err(
                ErrorCode::MalformedXml,
                path,
                "Comment contains forbidden `--` sequence",
            ));
        }
        self.pos += end + 3;
        Ok(())
    }

    fn skip_prolog_pi(&mut self, path: &str) -> Result<(), ModelError> {
        let rest = self.rest();
        if !rest.starts_with("<?xml") {
            return Err(self.err(
                ErrorCode::DisallowedXmlConstruct,
                path,
                "Processing instructions other than `<?xml` are disallowed",
            ));
        }
        let after_prefix = rest.as_bytes().get(5).copied();
        if !matches!(after_prefix, Some(b' ' | b'\t' | b'\r' | b'\n' | b'?')) {
            return Err(self.err(
                ErrorCode::DisallowedXmlConstruct,
                path,
                "Unsupported processing instruction prefix",
            ));
        }
        let Some(end) = rest.find("?>") else {
            return Err(self.err(
                ErrorCode::MalformedXml,
                path,
                "Unterminated XML declaration",
            ));
        };
        self.pos += end + 2;
        Ok(())
    }

    fn check_disallowed_bang(&self, path: &str) -> Result<(), ModelError> {
        let rest = self.rest();
        for forbidden in [
            "<!DOCTYPE",
            "<!ENTITY",
            "<!NOTATION",
            "<![CDATA[",
            "<!ELEMENT",
            "<!ATTLIST",
        ] {
            if rest.starts_with(forbidden) {
                return Err(self.err(
                    ErrorCode::DisallowedXmlConstruct,
                    path,
                    format!("Disallowed XML construct: {forbidden}"),
                ));
            }
        }
        if rest.starts_with("<!") && !rest.starts_with("<!--") {
            return Err(self.err(
                ErrorCode::DisallowedXmlConstruct,
                path,
                "Unsupported `<!` declaration",
            ));
        }
        Ok(())
    }

    fn parse_name(&mut self, path: &str) -> Result<&'a str, ModelError> {
        let start = self.pos;
        let rest = self.rest();
        let mut end_rel = 0usize;
        for (idx, ch) in rest.char_indices() {
            let valid = if idx == 0 {
                ch.is_ascii_alphabetic() || ch == '_' || ch == ':'
            } else {
                ch.is_ascii_alphanumeric() || matches!(ch, '_' | '-' | '.' | ':')
            };
            if valid {
                end_rel = idx + ch.len_utf8();
            } else {
                break;
            }
        }
        if end_rel == 0 {
            return Err(self.err(ErrorCode::MalformedXml, path, "Expected XML name"));
        }
        self.pos = start + end_rel;
        Ok(&self.src[start..self.pos])
    }

    fn decode_entities(&self, raw: &str, path: &str) -> Result<String, ModelError> {
        if !raw.contains('&') {
            return Ok(raw.to_owned());
        }
        let mut out = String::with_capacity(raw.len());
        let mut idx = 0usize;
        while idx < raw.len() {
            if let Some(rel_amp) = raw[idx..].find('&') {
                out.push_str(&raw[idx..idx + rel_amp]);
                let after = idx + rel_amp + 1;
                let Some(rel_semi) = raw[after..].find(';') else {
                    return Err(self.err(
                        ErrorCode::MalformedXml,
                        path,
                        "Unescaped `&` in XML text or attribute",
                    ));
                };
                let entity = &raw[after..after + rel_semi];
                match entity {
                    "amp" => out.push('&'),
                    "lt" => out.push('<'),
                    "gt" => out.push('>'),
                    "quot" => out.push('"'),
                    "apos" => out.push('\''),
                    _ if entity.starts_with('#') => {
                        let ch = parse_char_ref(entity).ok_or_else(|| {
                            self.err(
                                ErrorCode::MalformedXml,
                                path,
                                "Invalid XML character reference",
                            )
                        })?;
                        out.push(ch);
                    }
                    _ => {
                        return Err(self.err(
                            ErrorCode::DisallowedXmlConstruct,
                            path,
                            format!("Unknown or disallowed entity reference `&{entity};`"),
                        ));
                    }
                }
                idx = after + rel_semi + 1;
            } else {
                out.push_str(&raw[idx..]);
                break;
            }
        }
        Ok(out)
    }

    fn parse_attr_value(&mut self, path: &str) -> Result<String, ModelError> {
        let Some(quote) = self.bytes.get(self.pos).copied() else {
            return Err(self.err(ErrorCode::MalformedXml, path, "Expected attribute quote"));
        };
        if quote != b'"' && quote != b'\'' {
            return Err(self.err(
                ErrorCode::MalformedXml,
                path,
                "Expected quoted attribute value",
            ));
        }
        self.pos += 1;
        let q_char = quote as char;
        let rest = self.rest();
        let Some(rel_end) = rest.find(q_char) else {
            return Err(self.err(
                ErrorCode::MalformedXml,
                path,
                "Unterminated attribute value",
            ));
        };
        let raw = &rest[..rel_end];
        if raw.contains('<') {
            return Err(self.err(
                ErrorCode::MalformedXml,
                path,
                "Unescaped `<` inside attribute value",
            ));
        }
        self.pos += rel_end + 1;
        self.decode_entities(raw, path)
    }

    fn parse_element(
        &mut self,
        depth: usize,
        parent_ns: &NsScope,
        path: &str,
    ) -> Result<XmlNode, ModelError> {
        if depth > MAX_XML_DEPTH {
            return Err(self.err(
                ErrorCode::SizeLimitExceeded,
                path,
                "XML element nesting exceeds maximum depth",
            ));
        }
        self.elements += 1;
        if self.elements > MAX_XML_ELEMENTS {
            return Err(self.err(
                ErrorCode::SizeLimitExceeded,
                path,
                "XML element count exceeds maximum bound",
            ));
        }
        if !self.starts_with("<") {
            return Err(self.err(ErrorCode::MalformedXml, path, "Expected `<`"));
        }
        self.pos += 1;
        let raw_name = self.parse_name(path)?.to_owned();
        let elem_path = format!("{path}/{raw_name}");

        let mut ns_scope = parent_ns.clone();
        let mut raw_attrs = BTreeMap::new();
        let mut attr_count = 0usize;

        loop {
            let before_ws = self.pos;
            self.skip_ws();
            if self.starts_with("/>") || self.starts_with(">") {
                break;
            }
            if self.pos == before_ws {
                return Err(self.err(
                    ErrorCode::MalformedXml,
                    &elem_path,
                    "Expected whitespace before attribute or tag close",
                ));
            }
            attr_count += 1;
            if attr_count > MAX_XML_ATTRIBUTES {
                return Err(self.err(
                    ErrorCode::SizeLimitExceeded,
                    &elem_path,
                    "Element exceeds maximum attribute count",
                ));
            }
            let attr_name = self.parse_name(&elem_path)?.to_owned();
            self.skip_ws();
            if self.bytes.get(self.pos) != Some(&b'=') {
                return Err(self.err(
                    ErrorCode::MalformedXml,
                    &elem_path,
                    format!("Expected `=` after attribute `{attr_name}`"),
                ));
            }
            self.pos += 1;
            self.skip_ws();
            let attr_val = self.parse_attr_value(&elem_path)?;
            if raw_attrs.contains_key(&attr_name) {
                return Err(self.err(
                    ErrorCode::MalformedXml,
                    &elem_path,
                    format!("Duplicate XML attribute `{attr_name}`"),
                ));
            }
            raw_attrs.insert(attr_name, attr_val);
        }

        let mut attributes = BTreeMap::new();
        for (name, value) in raw_attrs {
            if name == "xmlns" {
                ns_scope.insert(String::new(), value);
            } else if let Some(prefix) = name.strip_prefix("xmlns:") {
                if prefix.is_empty() || value.is_empty() {
                    return Err(self.err(
                        ErrorCode::MalformedXml,
                        &elem_path,
                        "Namespace prefix and URI must be non-empty",
                    ));
                }
                ns_scope.insert(prefix.to_owned(), value);
            } else {
                attributes.insert(name, value);
            }
        }

        let (namespace, local_name) = resolve_qname(&raw_name, &ns_scope, &elem_path)?;

        if self.starts_with("/>") {
            self.pos += 2;
            return Ok(XmlNode {
                namespace,
                local_name,
                raw_name,
                attributes,
                children: Vec::new(),
                text: String::new(),
            });
        }
        self.pos += 1; // consume '>'

        let mut children = Vec::new();
        let mut text = String::new();

        loop {
            if self.pos >= self.src.len() {
                return Err(self.err(
                    ErrorCode::MalformedXml,
                    &elem_path,
                    format!("Unclosed XML element `{raw_name}`"),
                ));
            }
            if let Some(rel_lt) = self.rest().find('<') {
                if rel_lt > 0 {
                    let chunk = &self.rest()[..rel_lt];
                    text.push_str(&self.decode_entities(chunk, &elem_path)?);
                    self.pos += rel_lt;
                }
            } else {
                return Err(self.err(
                    ErrorCode::MalformedXml,
                    &elem_path,
                    format!("Unclosed XML element `{raw_name}`"),
                ));
            }

            if self.starts_with("</") {
                self.pos += 2;
                let close_name = self.parse_name(&elem_path)?;
                self.skip_ws();
                if self.bytes.get(self.pos) != Some(&b'>') {
                    return Err(self.err(
                        ErrorCode::MalformedXml,
                        &elem_path,
                        "Expected `>` in closing tag",
                    ));
                }
                self.pos += 1;
                if close_name != raw_name {
                    return Err(self.err(
                        ErrorCode::MalformedXml,
                        &elem_path,
                        format!("Mismatched closing tag `</{close_name}>` for `<{raw_name}>`"),
                    ));
                }
                break;
            } else if self.starts_with("<!--") {
                self.skip_comment(&elem_path)?;
            } else if self.starts_with("<?") {
                return Err(self.err(
                    ErrorCode::DisallowedXmlConstruct,
                    &elem_path,
                    "Processing instruction inside XML body is disallowed",
                ));
            } else if self.starts_with("<!") {
                self.check_disallowed_bang(&elem_path)?;
            } else {
                let child = self.parse_element(depth + 1, &ns_scope, &elem_path)?;
                children.push(child);
            }
        }

        Ok(XmlNode {
            namespace,
            local_name,
            raw_name,
            attributes,
            children,
            text,
        })
    }
}

fn parse_char_ref(entity: &str) -> Option<char> {
    let digits = entity.strip_prefix('#')?;
    let code = if let Some(hex) = digits.strip_prefix('x') {
        if hex.is_empty() {
            return None;
        }
        u32::from_str_radix(hex, 16).ok()?
    } else {
        if digits.is_empty() {
            return None;
        }
        digits.parse::<u32>().ok()?
    };
    let valid_xml_char =
        matches!(code, 0x09 | 0x0A | 0x0D | 0x20..=0xD7FF | 0xE000..=0xFFFD | 0x10000..=0x10FFFF);
    if !valid_xml_char {
        return None;
    }
    char::from_u32(code)
}

fn resolve_qname(
    raw_name: &str,
    ns_scope: &NsScope,
    path: &str,
) -> Result<(Option<String>, String), ModelError> {
    if let Some((prefix, local)) = raw_name.split_once(':') {
        if prefix.is_empty() || local.is_empty() || local.contains(':') {
            return Err(ModelError::new(
                ErrorCode::MalformedXml,
                path,
                format!("Invalid qualified XML name `{raw_name}`"),
            ));
        }
        let uri = ns_scope.get(prefix).ok_or_else(|| {
            ModelError::new(
                ErrorCode::MalformedXml,
                path,
                format!("Unbound XML namespace prefix `{prefix}`"),
            )
        })?;
        Ok((Some(uri.clone()), local.to_owned()))
    } else {
        Ok((ns_scope.get("").cloned(), raw_name.to_owned()))
    }
}

/// Parse UTF-8 XML bytes into a bounded DOM tree, failing closed on disallowed XML features.
pub fn parse_xml_bytes(bytes: &[u8]) -> Result<XmlNode, ModelError> {
    if bytes.len() > MAX_XML_BYTES {
        return Err(ModelError::new(
            ErrorCode::SizeLimitExceeded,
            "/xml",
            format!("XML input exceeds {} byte limit", MAX_XML_BYTES),
        ));
    }
    let src = std::str::from_utf8(bytes)
        .map_err(|_| ModelError::new(ErrorCode::MalformedXml, "/xml", "XML input is not UTF-8"))?;

    let mut parser = Parser::new(src);
    let mut seen_decl = false;
    loop {
        parser.skip_ws();
        if parser.starts_with("<!--") {
            parser.skip_comment("/xml")?;
        } else if parser.starts_with("<?") {
            if seen_decl {
                return Err(ModelError::new(
                    ErrorCode::DisallowedXmlConstruct,
                    "/xml",
                    "Duplicate or misplaced XML processing instruction",
                ));
            }
            parser.skip_prolog_pi("/xml")?;
            seen_decl = true;
        } else if parser.starts_with("<!") {
            parser.check_disallowed_bang("/xml")?;
        } else {
            break;
        }
    }

    if parser.pos >= src.len() || !parser.starts_with("<") {
        return Err(ModelError::new(
            ErrorCode::MalformedXml,
            "/xml",
            "Missing root XML element",
        ));
    }

    let root = parser.parse_element(1, &NsScope::new(), "")?;

    loop {
        parser.skip_ws();
        if parser.pos >= src.len() {
            break;
        }
        if parser.starts_with("<!--") {
            parser.skip_comment("/xml")?;
        } else if parser.starts_with("<!") {
            parser.check_disallowed_bang("/xml")?;
        } else {
            return Err(ModelError::new(
                ErrorCode::MalformedXml,
                "/xml",
                "Unexpected trailing content after root XML element",
            ));
        }
    }

    Ok(root)
}
