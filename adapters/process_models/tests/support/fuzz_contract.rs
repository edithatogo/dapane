//! Shared invariants for deterministic regression and coverage-guided campaigns.
use dapane_process_models::bpmn::{BpmnProfile, parse_bpmn_bytes, parse_bpmn_config};
use dapane_process_models::json_io::parse_json_bytes;
use dapane_process_models::pnml::{parse_pnml_bytes, parse_pnml_config};
use dapane_process_models::xml::{
    MAX_XML_ATTRIBUTES, MAX_XML_BYTES, MAX_XML_DEPTH, MAX_XML_ELEMENTS, parse_xml_bytes,
};

pub fn check(data: &[u8]) {
    if data.len() > MAX_XML_BYTES + 1 {
        return;
    }
    let xml = parse_xml_bytes(data);
    assert_eq!(
        xml,
        parse_xml_bytes(data),
        "XML parsing must be deterministic"
    );
    if let Ok(root) = xml {
        let mut pending = vec![(&root, 0_usize)];
        let mut count = 0;
        while let Some((node, depth)) = pending.pop() {
            count += 1;
            assert!(depth <= MAX_XML_DEPTH);
            assert!(node.attributes.len() <= MAX_XML_ATTRIBUTES);
            assert!(!node.local_name.is_empty());
            pending.extend(node.children.iter().map(|child| (child, depth + 1)));
        }
        assert!(count <= MAX_XML_ELEMENTS);
    }
    let json = parse_json_bytes(data);
    if let Ok(value) = json {
        let encoded = value.to_compact_string();
        assert_eq!(parse_json_bytes(encoded.as_bytes()), Ok(value));
    }
    let pnml = parse_pnml_bytes(data);
    assert_eq!(pnml, parse_pnml_bytes(data));
    if let Ok(net) = pnml {
        for arc in &net.arcs {
            assert!(arc.weight > 0);
            assert!(
                (net.places.contains_key(&arc.source) && net.transitions.contains_key(&arc.target))
                    || (net.transitions.contains_key(&arc.source)
                        && net.places.contains_key(&arc.target))
            );
        }
    }
    let _ = parse_bpmn_bytes(data, BpmnProfile::CoreAcyclic);
    let _ = parse_bpmn_bytes(data, BpmnProfile::ExtendedReworkSubprocess);
    let _ = parse_pnml_config(data);
    let _ = parse_bpmn_config(data);
}
