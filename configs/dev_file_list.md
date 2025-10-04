__init__.py
boot/__init__.py
boot/boot_exception_logger.py
boot/boot_path_initializer.py
boot/boot_phase_loader.py
boot/boot_trace_logger.py
boot/README.md
Canonical_CLI_Tool_Template.py
Canonical_Reflex_Template.py
configs/__init__.py
configs/build_log.json
configs/cron_schedule.json
configs/dev_bot_bootstrap.md
configs/dev_bot_instructions.md
configs/dev_file_list.md
configs/dev_file_list_template.md
configs/dev_notes.md
configs/file_safe_imports.json
configs/FlowMaster_OG_dev_file.md
configs/folder_roles.json
configs/ironroot_file_history_with_dependencies.json
configs/ironroot_history_template.json
configs/ironroot_manifest_data.json
configs/ironroot_manifest_template.json
configs/Phase_02_DevBot_Completion_Debrief.md
configs/Phase_02_file_list.json
configs/Phase_03_file_list.json
configs/Phase_04_file_list.json
configs/phase_history.json
configs/phase_stabilization_templates.md
core/__init__.py
core/manifest_db.py
core/memory_interface.py
core/memory_log_db.py
core/phase_control.py
core/reflex_registry_db.py
core/snapshot_manager.py
core/sqlite_bootstrap.py
core/trace_logger.py
logs/boot_trace_log.json
logs/reflex_trace_log.json
logs/will_memory_log.json
reflexes/reflex_core/__init__.py
reflexes/reflex_core/reflex_loader.py
reflexes/reflex_core/reflex_self_test_runner.py
reflexes/reflex_core/reflex_table_tick.py
reflexes/reflex_core/reflex_trace_ping.py
root/test.json
sandbox/__init__.py
sandbox/sandbox_reflex_tests.py
seeds/__init__.py
seeds/business/branding_tone_seed.md
seeds/business/business_communication_seed.md
seeds/business/client_profile_seed.md
seeds/business/ironroot_mission_seed.md
seeds/business/market_research_seed.md
seeds/business/monetization_strategy_seed.md
seeds/business/phase_map_seed.md
seeds/business/project_index_seed.md
seeds/business/reflex_catalog_seed.md
seeds/business/usage_policy_seed.md
seeds/core/seed_ironroot_summary.md
seeds/core/seed_ironroot_summary.txt
seeds/core/seed_operator_preferences.md
seeds/core/seed_origin_story.md
seeds/engineering/api_surface_seed.md
seeds/engineering/architecture_principles_seed.md
seeds/engineering/cli_templates_seed.md
seeds/engineering/ironroot_law_seed.md
seeds/engineering/logging_conventions_seed.md
seeds/engineering/memory_schema_seed.md
seeds/engineering/module_layout_seed.md
seeds/engineering/phase_gate_seed.md
seeds/engineering/reflex_compliance_seed.md
seeds/engineering/testing_strategy_seed.md
seeds/engineering/trace_pipeline_seed.md
seeds/engineering/utf8_policy_seed.md
seeds/optional/agent_personas_seed.md
seeds/optional/automation_loops_seed.md
seeds/optional/cron_jobs_seed.md
seeds/optional/data_backup_seed.md
seeds/optional/debug_macros_seed.md
seeds/optional/error_taxonomy_seed.md
seeds/optional/experiment_toggles_seed.md
seeds/optional/feature_flags_seed.md
seeds/optional/file_sentinel_seed.md
seeds/optional/goal_templates_seed.md
seeds/optional/maintenance_playbooks_seed.md
seeds/optional/metric_events_seed.md
seeds/optional/ops_runbooks_seed.md
seeds/optional/persona_seed.md
seeds/optional/proxy_rules_seed.md
seeds/optional/task_template_seed.md
seeds/optional/time_awareness_seed.md
seeds/reflex_manifest.json
seeds/security/api_key_handling_seed.md
seeds/security/autonomy_limits_seed.md
seeds/security/data_retention_seed.md
seeds/security/log_redaction_seed.md
seeds/security/privacy_guard_seed.md
seeds/security/reflex_sandbox_seed.md
seeds/security/safety_protocol_seed.md
seeds/seed_identity.py
seeds/seed_ironroot_summary.py
seeds/seed_operator_preferences.py
seeds/seed_origin_story.py
seeds/startup_manifest.yaml
tests/__init__.py
tests/test_phase_0_1_db_integrity.py
tests/test_phase_0_2_db_lifecycle.py
tests/test_phase_0_3_integrity.py
tests/test_phase_0_5_snapshot_diffs.py
tests/test_phase_0_5_trace_memory_integrity.py
tests/test_phase_0_integrity.py
tools/__init__.py
tools/auto_reg_probe.py
tools/check_db_tables.py
tools/db_snapshot_auditor.py
tools/fix_file_encoding.py
tools/git_hooks_precommit.py
tools/hello_ironroot_tool.py
tools/hook_probe.py
tools/ingest_seeds.py
tools/ironroot_registrar.py
tools/manifest_diff.py
tools/manifest_history_auditor.py
tools/manifest_sync.py
tools/path_validator.py
tools/phase_0_5_sealer.py
tools/phase_guard_sweep.py
tools/phase_trace_report.py
tools/print_current_phase.py
tools/reflex_compliance_guard.py
tools/snapshot_db.py
tools/system_check.py
tools/test_memory_logger.py
tools/tools_check_db_counts.py
tools/tools_check_dupes.py
tools/tools_check_memory_log_calls.py
tools/tools_check_utf8_encoding.py
tools/trace_inspector.py
tools/trace_memory_alignment.py
tools/trace_memory_crosscheck.py
tools/trace_memory_snapshot.py
tools/update_phase_tracking.py
tools/verify_log_integrity.py
tools/will_cli.py
will_commands.md
will_commands_reference.md
will_commands_samples.md
will_data.db

<!-- auto:ironroot_registrar -->
- tests/test_phase_0_6_api_smoke.py

<!-- auto:ironroot_registrar -->
- tests/test_phase_0_6_auto_migration_roundtrip.py

<!-- auto:ironroot_registrar -->
- tests/test_phase_0_6_preseal_end_to_end.py

<!-- auto:ironroot_registrar -->
- tests/test_phase_0_6_schema_contract.py

<!-- auto:ironroot_registrar -->
- tools/api_smoke_suite.py

<!-- auto:ironroot_registrar -->
- tools/db_schema_contract.py

<!-- auto:ironroot_registrar -->
- tools/db_schema_migrate.py

<!-- auto:ironroot_registrar -->
- tools/phase_0_6_sealer.py

<!-- auto:ironroot_registrar -->
- tools/run_all_phase_tests.py

<!-- auto:ironroot_registrar -->
- files

<!-- auto:ironroot_registrar -->
- tools/ask_server.py

<!-- auto:ironroot_registrar -->
- tools/ask_server_mirror.py

<!-- auto:ironroot_registrar -->
- tools/ask_will.py

<!-- auto:ironroot_registrar -->
- tools/audit/will_inventory_probe.py

<!-- auto:ironroot_registrar -->
- tools/auto_phase_guard_fix.py

<!-- auto:ironroot_registrar -->
- tools/autosave/__init__.py

<!-- auto:ironroot_registrar -->
- tools/autosave/autosave_helper.py

<!-- auto:ironroot_registrar -->
- tools/autosave/local_listener.py

<!-- auto:ironroot_registrar -->
- tools/autosave/userscripts/__init__.py

<!-- auto:ironroot_registrar -->
- tools/chunker/chunker.py

<!-- auto:ironroot_registrar -->
- tools/chunker/chunker_cli.py

<!-- auto:ironroot_registrar -->
- tools/chunker/inspect_chunk_db.py

<!-- auto:ironroot_registrar -->
- tools/chunker/migrate_backfill_chunk_hashes.py

<!-- auto:ironroot_registrar -->
- tools/chunker/summarize_and_index_reflex.py

<!-- auto:ironroot_registrar -->
- tools/file_history_backfill_all.py

<!-- auto:ironroot_registrar -->
- tools/model_router.py

<!-- auto:ironroot_registrar -->
- tools/reflex_coverage_report.py

<!-- auto:ironroot_registrar -->
- tools/reflex_registry_scanner.py

<!-- auto:ironroot_registrar -->
- tools/reposition_phase_guard.py

<!-- auto:ironroot_registrar -->
- tools/retriever.py

<!-- auto:ironroot_registrar -->
- tools/will_browser.py

<!-- auto:ironroot_registrar -->
- tools/will_search_panel.py

<!-- auto:ironroot_registrar -->
- tools/artifact_emitter.py
