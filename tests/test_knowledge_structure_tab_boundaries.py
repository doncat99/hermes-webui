from pathlib import Path
from urllib.parse import urlparse
import re


REPO = Path(__file__).parent.parent
HTML = (REPO / "static" / "index.html").read_text(encoding="utf-8")
PANELS_JS = (REPO / "static" / "panels.js").read_text(encoding="utf-8")
I18N_JS = (REPO / "static" / "i18n.js").read_text(encoding="utf-8")
ROUTES_PY = (REPO / "api" / "routes.py").read_text(encoding="utf-8")
STYLE_CSS = (REPO / "static" / "style.css").read_text(encoding="utf-8")
BOOT_JS = (REPO / "static" / "boot.js").read_text(encoding="utf-8")


def test_knowledge_structure_tab_is_registered_and_operator_visible():
    compact = PANELS_JS.replace(" ", "")

    assert "knowledgeStructure:'tab_knowledge_structure'" in compact
    assert "if(nextPanel==='knowledgeStructure'){awaitmountKnowledgeStructurePanel();awaitloadKnowledgeStructure();}" in compact
    assert "'knowledgeStructure'" in PANELS_JS
    assert 'data-panel="knowledgeStructure"' in HTML
    assert 'id="panelKnowledgeStructure"' in HTML
    assert 'id="mainKnowledgeStructure"' in HTML
    assert 'id="knowledgeStructureSidebar"' in HTML
    assert 'id="knowledgeStructureContent"' in HTML
    assert 'data-i18n="knowledge_structure_title"' in HTML
    assert "tab_knowledge_structure" in I18N_JS
    assert "knowledge_structure_title" in I18N_JS


def test_knowledge_structure_uses_mount_load_patch_contract():
    assert "async function mountKnowledgeStructurePanel()" in PANELS_JS
    assert "async function loadKnowledgeStructureData(mode)" in PANELS_JS
    assert "async function patchKnowledgeStructureView(prev, next, mode)" in PANELS_JS
    assert "await _runPanelRefresh('knowledgeStructure'" in PANELS_JS


def _function_body(source, function_name):
    start = source.index(f"function {function_name}")
    end = source.find("\nfunction ", start + 1)
    if end == -1:
        end = len(source)
    return source[start:end]


def test_knowledge_structure_sidebar_uses_global_shell_column():
    shell_sidebar = re.search(r'<aside\s+class="sidebar"', HTML)
    assert shell_sidebar, "global shell <aside class=\"sidebar\"> must exist in index.html"
    assert HTML.index('<nav class="rail"') < shell_sidebar.start(), (
        "far-left icon rail must remain before the global shell sidebar"
    )
    assert 'id="panelKnowledgeStructure"' in HTML
    assert 'id="knowledgeStructureSidebar"' in HTML
    assert "knowledgeStructureSidebar" in PANELS_JS
    assert "Knowledge Structure context and scope" in PANELS_JS
    assert "Context and Scope" in PANELS_JS


def test_knowledge_structure_activation_keeps_global_shell_sidebar_available():
    switch_body = _function_body(PANELS_JS, "switchPanel")
    assert "knowledge-structure-shell-collapsed" not in switch_body

    is_collapsed_body = _function_body(BOOT_JS, "_isSidebarCollapsed")
    assert "knowledge-structure-shell-collapsed" not in is_collapsed_body
    sync_aria_body = _function_body(BOOT_JS, "_syncSidebarAria")
    assert ".rail .rail-btn.nav-tab.active[data-panel]" in sync_aria_body
    assert "aria-expanded" in sync_aria_body


def test_knowledge_structure_ui_exposes_read_model_boundaries_and_fail_closed_actions():
    assert "Knowledge Structure workbench" in PANELS_JS
    assert "Knowledge item browser" in PANELS_JS
    assert "Knowledge item inspector" in PANELS_JS
    assert "Proposal draft / review lane" in PANELS_JS
    assert "Proposal edits do not mutate governed truth" in PANELS_JS
    assert "Accepted knowledge is read-only here" in PANELS_JS
    assert "Proposal drafting disabled" in PANELS_JS
    assert "Submit for promotion review disabled" in PANELS_JS
    assert "setKnowledgeStructureFilter(" in PANELS_JS
    assert "_filterKnowledgeStructureItems(" in PANELS_JS
    assert "platform_reusable" in PANELS_JS
    assert "anti_pattern" in PANELS_JS
    assert "Propose edit" in PANELS_JS
    assert "Propose deprecation" in PANELS_JS
    assert "Propose merge/split/refactor" in PANELS_JS
    assert "<button type=\"button\" disabled>Propose edit</button>" in PANELS_JS
    assert "<button type=\"button\" disabled>Propose deprecation</button>" in PANELS_JS
    assert "<button type=\"button\" disabled>Propose merge/split/refactor</button>" in PANELS_JS
    assert "knowledge-structure-degraded" in STYLE_CSS


def test_knowledge_structure_badge_does_not_treat_optional_proposal_store_as_global_degraded():
    badge_fn = _function_body(PANELS_JS, "_knowledgeFreshnessBadge")
    assert "canonical_source_status" in badge_fn, (
        "Freshness badge should consult canonical source status rather than "
        "blindly degrading on any optional store being unavailable."
    )
    assert "degraded_reasons" in badge_fn, (
        "Freshness badge should use backend degraded reasons for true canonical-truth degradation."
    )
    assert "proposal_store_status" not in badge_fn.split("return {cls:'err', text:'degraded'}")[0], (
        "Optional proposal-store unavailability must not be enough to mark the whole knowledge view degraded."
    )


def test_knowledge_structure_ui_exposes_context_scope_rail_and_browse_adjacent_filters():
    assert "Knowledge Structure context and scope" in PANELS_JS
    assert "Context and Scope" in PANELS_JS
    assert "All knowledge" in PANELS_JS
    assert "Accepted governed truth" in PANELS_JS
    assert "Proposal overlay" in PANELS_JS
    assert "Promotion accountability" in PANELS_JS
    assert "Canonical absence" in PANELS_JS
    assert "Runtime evidence only" in PANELS_JS
    assert "Platform reusable" in PANELS_JS
    assert "Project learning" in PANELS_JS
    assert "Anti-patterns" in PANELS_JS
    assert "Source health" in PANELS_JS
    assert "knowledgeStructureSidebar.innerHTML" in PANELS_JS
    assert "knowledge-structure-context-rail" in STYLE_CSS
    assert "Browse filters" in PANELS_JS
    assert "knowledge-structure-filters" in PANELS_JS
    assert "setKnowledgeStructureFilter(" in PANELS_JS
    assert "setKnowledgeStructureContextPivot(" in PANELS_JS


def test_knowledge_structure_layout_preserves_sidebar_then_browse_inspect_order():
    sidebar_pos = PANELS_JS.index("knowledgeStructureSidebar.innerHTML")
    rail_pos = PANELS_JS.index('class="knowledge-structure-context-rail"', sidebar_pos)
    filters_pos = PANELS_JS.index('class="knowledge-structure-filters"', sidebar_pos)
    workbench_pos = PANELS_JS.index('class="knowledge-structure-workbench"')
    grid_pos = PANELS_JS.index('class="knowledge-structure-grid"', workbench_pos)
    browser_pos = PANELS_JS.index('class="knowledge-structure-browser"', grid_pos)
    inspector_pos = PANELS_JS.index('class="knowledge-structure-inspector"', browser_pos)
    proposal_pos = PANELS_JS.index('class="knowledge-structure-proposal-rail"', inspector_pos)

    assert sidebar_pos < rail_pos < filters_pos
    assert workbench_pos < grid_pos
    assert grid_pos < browser_pos < inspector_pos < proposal_pos


def test_knowledge_structure_responsive_contract_protects_browse_and_inspect_width():
    compact_css = STYLE_CSS.replace(" ", "")

    assert ".knowledge-structure-grid{display:grid;grid-template-columns:minmax(320px,1fr)minmax(340px,.85fr)" in compact_css
    assert "@media(max-width:1100px){.knowledge-structure-grid{grid-template-columns:1fr;" in compact_css
    assert ".knowledge-structure-filters{grid-template-columns:repeat(2,minmax(130px,1fr));" in compact_css


def test_knowledge_structure_selected_item_workflow_is_no_loss_across_filters():
    assert "if (!_knowledgeStructureSelectedItemId && items.length) _knowledgeStructureSelectedItemId = items[0].item_id;" in PANELS_JS
    assert "if (_knowledgeStructureSelectedItemId && !items.some(item => item.item_id === _knowledgeStructureSelectedItemId))" in PANELS_JS
    assert "_knowledgeStructureSelectedItemId = items[0] ? items[0].item_id : null;" in PANELS_JS
    assert "let selectedId = _knowledgeStructureSelectedItemId || (filteredItems[0] && filteredItems[0].item_id) || '';" in PANELS_JS
    assert "if (selectedId && !filteredItems.some(item => item.item_id === selectedId))" in PANELS_JS
    assert "selectedId = filteredItems[0] ? filteredItems[0].item_id : null;" in PANELS_JS
    assert "_knowledgeStructureSelectedItemId = selectedId;" in PANELS_JS
    assert "async function selectKnowledgeStructureItem(itemId)" in PANELS_JS
    assert "_knowledgeStructureSelectedItemId = itemId;" in PANELS_JS


def test_knowledge_structure_api_model_payload_contract(monkeypatch):
    import api.routes as routes

    captured = []
    monkeypatch.setattr(routes, "j", lambda _handler, payload, status=200, extra_headers=None: captured.append((status, payload)) or True)

    result = routes._handle_knowledge_structure_get(
        object(),
        urlparse("/api/knowledge-structure/model?project_key=knowledge_governance_console"),
    )

    assert result is True
    status, payload = captured[-1]
    assert status == 200
    assert payload["project_key"] == "knowledge_governance_console"
    assert payload["generated_at"]

    freshness = payload["freshness"]
    assert freshness["index_status"] in {"fresh", "stale", "rebuilding", "unavailable"}
    assert freshness["governed_store_status"] in {"fresh", "stale", "rebuilding", "unavailable"}
    assert freshness["proposal_store_status"] == "unavailable"
    assert freshness["evidence_status"] in {"fresh", "stale", "rebuilding", "unavailable"}

    capabilities = payload["capabilities"]
    assert capabilities["can_create_proposal"] is False
    assert capabilities["can_submit_for_promotion"] is False
    assert capabilities["can_view_provenance"] is True
    assert "accepted-truth mutation remain disabled" in capabilities["degraded_notice"].lower() or "writes fail closed" in capabilities["degraded_notice"].lower()
    assert "proposal/review only" in capabilities["write_boundary"].lower()

    items = payload["items"]
    assert items, "read-model browse payload must expose knowledge rows"
    required_item_fields = {
        "item_id",
        "title",
        "summary",
        "item_type",
        "lifecycle",
        "truth_status",
        "distillation_category",
        "distillation_scope",
        "governance_decision",
        "proposed_by",
        "source_count",
        "relationship_count",
        "has_pending_change",
        "updated_at",
    }
    for item in items:
        assert required_item_fields <= set(item)
    assert any(item["lifecycle"] == "accepted" and item["truth_status"] == "governed" for item in items)
    assert any(item["has_pending_change"] is True for item in items)

    filters = payload["filters"]
    assert {"accepted", "superseded", "merged", "split", "refactored"} <= set(filters["lifecycle"])
    assert {"governed", "proposal_overlay", "derived_index", "runtime_evidence_only"} <= set(filters["truth_status"])
    assert {"platform_reusable", "project_learning", "anti_pattern", "none"} & set(filters["distillation_category"])
    assert {"platform", "project", "none"} & set(filters["distillation_scope"])
    assert {"stale", "unavailable"} <= set(filters["freshness_state"])

    proposals = payload["pending_proposals"]
    assert isinstance(proposals, list)
    if proposals:
        assert {"proposal_id", "operation", "workflow_state", "target_item_ids", "provenance_ids"} <= set(proposals[0])


def test_knowledge_structure_model_can_surface_promotion_candidates_from_truth(monkeypatch):
    import api.routes as routes

    captured = []
    monkeypatch.setattr(routes, "j", lambda _handler, payload, status=200, extra_headers=None: captured.append((status, payload)) or True)
    synthetic = {
        "project_key": "knowledge_governance_console",
        "generated_at": "2026-05-15T00:00:00Z",
        "freshness": {
            "index_status": "fresh",
            "governed_store_status": "fresh",
            "proposal_store_status": "unavailable",
            "evidence_status": "fresh",
        },
        "capabilities": {
            "can_create_proposal": False,
            "can_submit_for_promotion": False,
            "can_view_provenance": True,
            "degraded_notice": "canonical truth only",
            "write_boundary": "proposal/review only",
        },
        "filters": {
            "lifecycle": ["all", "accepted", "proposed"],
            "item_type": ["all", "promotion_candidate"],
            "truth_status": ["all", "governed", "proposal_overlay"],
            "relationship_kind": ["all", "supports"],
            "proposal_state": ["all", "under_review"],
            "freshness_state": ["all", "fresh"],
            "distillation_category": ["all", "project_learning"],
            "distillation_scope": ["all", "project"],
            "governance_decision": ["all", "approve"],
        },
        "items": [
            {
                "item_id": "ks:promotion:kc.alpha.delivery_loop",
                "title": "kc.alpha.delivery_loop",
                "summary": "project_learning / project",
                "item_type": "promotion_candidate",
                "lifecycle": "accepted",
                "truth_status": "governed",
                "distillation_category": "project_learning",
                "distillation_scope": "project",
                "governance_decision": "approve",
                "proposed_by": "knowledge-steward",
                "source_count": 1,
                "relationship_count": 2,
                "has_pending_change": False,
                "updated_at": "2026-05-15T00:00:00Z",
                "provenance_ids": [],
                "canonical_absence": [],
                "governance_chain": [],
            }
        ],
        "pending_proposals": [
            {
                "proposal_id": "prop:1",
                "operation": "promotion_followup",
                "workflow_state": "under_review",
                "target_item_ids": ["ks:promotion:kc.alpha.delivery_loop"],
                "provenance_ids": [],
            }
        ],
    }
    monkeypatch.setattr(routes, "_knowledge_structure_build_model", lambda _project_key="knowledge_governance_console": synthetic)

    result = routes._handle_knowledge_structure_get(
        object(),
        urlparse("/api/knowledge-structure/model?project_key=knowledge_governance_console"),
    )

    assert result is True
    _, payload = captured[-1]
    assert any(item["item_type"] == "promotion_candidate" for item in payload["items"])
    assert any(item["distillation_category"] == "project_learning" for item in payload["items"])


def test_knowledge_structure_model_can_surface_catalog_promotions_when_project_view_has_none(monkeypatch):
    import api.routes as routes

    bundle = {
        "payloads": {
            "operator_status": {"knowledge_governance_flow": []},
            "project_data_catalog": {
                "status": "ready",
                "ready": True,
                "projects": {
                    "knowledge_governance_console": {
                        "status": "ready",
                        "ready": True,
                        "fact_count": 12,
                        "governed_data_asset_count": 0,
                    }
                },
                "promotion_accountability": [
                    {
                        "project_key": "alpha",
                        "candidate_key": "kc.project_application.alpha.demo_artifact",
                        "proposed_by": "designer",
                        "distillation_category": "project_learning",
                        "distillation_scope": "project",
                        "decision": "approve",
                        "allowed_approvers": ["knowledge-steward"],
                        "actual_decider": "knowledge-steward",
                        "application_status": "applied",
                        "write_back_status": "written",
                        "applied_by": "PromotionApplicationService",
                        "target_path": "projects/alpha/knowledge/application_artifacts/demo_artifact.yaml",
                        "evidence_refs": ["artifacts/runs/alpha/demo_artifact.validation.yaml"],
                        "source_refs": ["artifacts/runs/alpha/demo_artifact.packet.yaml"],
                    }
                ],
            },
            "project_data_view": {
                "status": "ready",
                "ready": True,
                "goal": {
                    "goal_key": "knowledge_governance_console.delivery_loop",
                    "goal_statement": "Every governed run leaves evidence.",
                },
                "ontology_facts": {
                    "fact_count": 12,
                    "subject_type_counts": {"Run": 1},
                    "predicate_counts": {"records_decision": 1},
                },
                "goal_alignment": {
                    "coverage": {
                        "required_fact_count": 1,
                        "met_requirement_count": 1,
                        "missing_requirement_count": 0,
                    },
                    "requirements": [
                        {
                            "requirement_key": "decision_trace",
                            "description": "Runs must record decisions.",
                            "status": "met",
                            "matching_fact_keys": ["fact.1"],
                        }
                    ],
                },
                "execution_projection": {
                    "latest_kanban_projection": {
                        "projection_status": "projected",
                        "board": "knowledge-governance",
                        "runtime_status": {"runtime_state": "running"},
                        "task_refs": [],
                    }
                },
                "promotion_observability": [],
            },
        },
        "paths": {},
        "errors": {},
    }
    monkeypatch.setattr(routes, "_knowledge_structure_truth_bundle", lambda _project_key: bundle)

    payload = routes._knowledge_structure_build_model("knowledge_governance_console")

    promotion_items = [
        item for item in payload["items"] if item["item_type"] == "promotion_candidate"
    ]
    assert promotion_items
    assert any(item["title"] == "kc.project_application.alpha.demo_artifact" for item in promotion_items)
    assert any(item["distillation_category"] == "project_learning" for item in promotion_items)


def test_knowledge_structure_detail_payload_exposes_provenance_relationships_lineage_and_boundary(monkeypatch):
    import api.routes as routes

    captured = []
    monkeypatch.setattr(routes, "j", lambda _handler, payload, status=200, extra_headers=None: captured.append((status, payload)) or True)
    model = routes._knowledge_structure_build_model("knowledge_governance_console")
    target = next(
        (item for item in model["items"] if item["truth_status"] in {"derived_index", "runtime_evidence_only", "governed"}),
        model["items"][0],
    )

    result = routes._handle_knowledge_structure_get(
        object(),
        urlparse(f"/api/knowledge-structure/items/{target['item_id'].replace(':', '%3A')}?project_key=knowledge_governance_console"),
    )

    assert result is True
    status, payload = captured[-1]
    assert status == 200
    assert payload["item"]["item_id"] == target["item_id"]
    assert payload["item"]["truth_status"] in {"derived_index", "runtime_evidence_only", "governed", "proposal_overlay", "canonical_absence"}
    assert payload["provenance"]
    assert {"provenance_id", "source_kind", "source_uri", "excerpt", "captured_at", "trust_level"} <= set(payload["provenance"][0])
    assert payload["relationships"]
    assert {"relationship_id", "kind", "from_item_id", "to_item_id", "status", "provenance_ids"} <= set(payload["relationships"][0])
    assert any(rel["kind"] == "derived_from" for rel in payload["relationships"])
    assert isinstance(payload["proposals"], list)
    assert payload["promotion_history"]
    assert payload["write_boundary"]["mode"] == "proposal_only"
    assert payload["write_boundary"]["accepted_truth_mutation_allowed"] is False


def test_knowledge_structure_promotion_detail_exposes_distillation_and_governance_chain(monkeypatch):
    import api.routes as routes

    captured = []
    monkeypatch.setattr(routes, "j", lambda _handler, payload, status=200, extra_headers=None: captured.append((status, payload)) or True)
    synthetic = {
        "project_key": "knowledge_governance_console",
        "generated_at": "2026-05-15T00:00:00Z",
        "freshness": {"index_status": "fresh"},
        "capabilities": {},
        "pending_proposals": [],
        "provenance_index": {
            "prov:promotion": {
                "provenance_id": "prov:promotion",
                "source_kind": "promotion_observability",
                "source_uri": "artifacts/ontology/knowledge_governance_console/project_data_view.json",
                "json_pointer": "/promotion_observability/0",
                "excerpt": "promotion row",
                "captured_at": "2026-05-15T00:00:00Z",
                "trust_level": "canonical",
            }
        },
        "relationships": [],
        "items": [
            {
                "item_id": "ks:promotion:kc.alpha.delivery_loop",
                "title": "kc.alpha.delivery_loop",
                "summary": "project_learning / project · approve by project_governance",
                "item_type": "promotion_candidate",
                "lifecycle": "accepted",
                "truth_status": "governed",
                "confidence": None,
                "source_count": 1,
                "relationship_count": 0,
                "has_pending_change": False,
                "updated_at": "2026-05-15T00:00:00Z",
                "provenance_ids": ["prov:promotion"],
                "canonical_absence": [],
                "governance_chain": [
                    {
                        "chain_id": "kc.alpha.delivery_loop",
                        "decision": "approve",
                        "actual_decider": "project_governance",
                        "application_status": "applied",
                        "write_back_status": "written",
                        "allowed_approvers": ["project_governance", "platform_governance"],
                    }
                ],
                "distillation_category": "project_learning",
                "distillation_scope": "project",
                "governance_decision": "approve",
                "proposed_by": "knowledge-steward",
            }
        ],
    }
    monkeypatch.setattr(routes, "_knowledge_structure_build_model", lambda _project_key="knowledge_governance_console": synthetic)

    result = routes._handle_knowledge_structure_get(
        object(),
        urlparse("/api/knowledge-structure/items/ks%3Apromotion%3Akc.alpha.delivery_loop?project_key=knowledge_governance_console"),
    )

    assert result is True
    status, payload = captured[-1]
    assert status == 200
    assert payload["item"]["item_type"] == "promotion_candidate"
    assert payload["item"]["distillation_category"] == "project_learning"
    assert payload["item"]["distillation_scope"] == "project"
    assert payload["governance_chain"]
    assert payload["governance_chain"][0]["actual_decider"] == "project_governance"


def test_knowledge_structure_provenance_and_relationship_subresources_include_freshness(monkeypatch):
    import api.routes as routes

    captured = []
    monkeypatch.setattr(routes, "j", lambda _handler, payload, status=200, extra_headers=None: captured.append((status, payload)) or True)
    model = routes._knowledge_structure_build_model("knowledge_governance_console")
    target = next((item for item in model["items"] if item["provenance_ids"]), model["items"][0])

    for suffix, key in [("provenance", "provenance"), ("relationships", "relationships")]:
        captured.clear()
        result = routes._handle_knowledge_structure_get(
            object(),
            urlparse(f"/api/knowledge-structure/items/{target['item_id'].replace(':', '%3A')}/{suffix}?project_key=knowledge_governance_console"),
        )
        assert result is True
        status, payload = captured[-1]
        assert status == 200
        assert payload["item_id"] == target["item_id"]
        assert payload[key]
        assert payload["freshness"]["index_status"] in {"fresh", "stale", "rebuilding", "unavailable"}
        assert payload["freshness"]["governed_store_status"] in {"fresh", "stale", "rebuilding", "unavailable"}


def test_knowledge_structure_get_unknown_item_fails_closed(monkeypatch):
    import api.routes as routes

    captured = []
    monkeypatch.setattr(routes, "bad", lambda _handler, msg, status=400: captured.append((status, msg)) or True)

    result = routes._handle_knowledge_structure_get(
        object(),
        urlparse("/api/knowledge-structure/items/ks%3Amissing"),
    )

    assert result is True
    status, message = captured[-1]
    assert status == 404
    assert "not found" in message.lower()


def test_knowledge_structure_posts_are_fail_closed_for_all_direct_mutations(monkeypatch):
    import api.routes as routes

    captured = []
    monkeypatch.setattr(routes, "bad", lambda _handler, msg, status=400: captured.append((status, msg)) or True)
    monkeypatch.setattr(routes, "_check_csrf", lambda _handler: True)
    monkeypatch.setattr(routes, "read_body", lambda _handler: {})

    mutation_paths = [
        "/api/knowledge-structure/items/ks:boundary:proposal-only/edit",
        "/api/knowledge-structure/items/ks:boundary:proposal-only/delete",
        "/api/knowledge-structure/items/ks:boundary:proposal-only/merge",
        "/api/knowledge-structure/items/ks:boundary:proposal-only/split",
        "/api/knowledge-structure/proposals",
        "/api/knowledge-structure/promotions/submit",
    ]
    for path in mutation_paths:
        captured.clear()
        result = routes.handle_post(object(), urlparse(path))
        assert result is True
        status, message = captured[-1]
        assert status == 423
        lowered = message.lower()
        assert "proposal/review-only" in lowered
        assert "accepted truth cannot be mutated" in lowered


def test_knowledge_structure_routes_are_wired_before_generic_api_fallbacks():
    assert 'if parsed.path.startswith("/api/knowledge-structure"):' in ROUTES_PY
    assert "result = _handle_knowledge_structure_get(handler, parsed)" in ROUTES_PY
    assert "unknown Knowledge Structure endpoint" in ROUTES_PY
    assert "Knowledge Structure writes are proposal/review-only" in ROUTES_PY
