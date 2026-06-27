// CommuneOS API — TypeScript types auto-generated from OpenAPI schema
// Do not edit manually. Source: GET /openapi.json

export interface HTTPValidationError {
  detail?: ValidationError[];
}

export interface ProgressUpdate {
  task_id: string;
  completed?: boolean;
  time_spent_minutes?: null | number;
  notes?: null | string;
}

export interface UserCreateRequest {
  user_id?: null | string;
  username: string;
  email?: null | string;
  bio?: null | string;
  tags?: string[];
  interests?: string[];
  goals?: string | string[];
  github_url?: null | string;
  linkedin_url?: null | string;
  timezone?: null | string;
}

export interface ValidationError {
  loc: number | string[];
  msg: string;
  type: string;
}

// ─── API Endpoint Map ───────────────────────────────────────────
export type ApiEndpoints = {
  // GET /  — Root
  'root__get': unknown;
  // POST /api/v1/agents/community/health  — Run Community Health
  'run_community_health_api_v1_agents_community_health_post': unknown;
  // POST /api/v1/agents/personalize/{user_id}  — Personalize Member
  'personalize_member_api_v1_agents_personalize__user_id__post': unknown;
  // POST /api/v1/agents/refresh/{user_id}  — Refresh Personalization
  'refresh_personalization_api_v1_agents_refresh__user_id__post': unknown;
  // GET /api/v1/agents/status/{user_id}  — Get Agent Status
  'get_agent_status_api_v1_agents_status__user_id__get': unknown;
  // GET /api/v1/community/gaps  — Get Community Gaps
  'get_community_gaps_api_v1_community_gaps_get': unknown;
  // GET /api/v1/community/members/at-risk  — Get At Risk Members
  'get_at_risk_members_api_v1_community_members_at_risk_get': unknown;
  // GET /api/v1/community/metrics  — Get Community Metrics
  'get_community_metrics_api_v1_community_metrics_get': unknown;
  // GET /api/v1/community/trends  — Get Community Trends
  'get_community_trends_api_v1_community_trends_get': unknown;
  // GET /api/v1/discovery/{user_id}/channels  — Get Recommended Channels
  'get_recommended_channels_api_v1_discovery__user_id__channels_get': unknown;
  // POST /api/v1/discovery/{user_id}/feedback  — Log Recommendation Feedback
  'log_recommendation_feedback_api_v1_discovery__user_id__feedback_post': unknown;
  // GET /api/v1/discovery/{user_id}/mentors  — Get Mentor Matches
  'get_mentor_matches_api_v1_discovery__user_id__mentors_get': unknown;
  // GET /api/v1/discovery/{user_id}/resources  — Get Recommended Resources
  'get_recommended_resources_api_v1_discovery__user_id__resources_get': unknown;
  // GET /api/v1/learning/{user_id}/checklist  — Get Daily Checklist
  'get_daily_checklist_api_v1_learning__user_id__checklist_get': unknown;
  // GET /api/v1/learning/{user_id}/milestones  — Get Milestones
  'get_milestones_api_v1_learning__user_id__milestones_get': unknown;
  // POST /api/v1/learning/{user_id}/progress  — Log Learning Progress
  'log_learning_progress_api_v1_learning__user_id__progress_post': unknown;
  // GET /api/v1/learning/{user_id}/roadmap  — Get Learning Roadmap
  'get_learning_roadmap_api_v1_learning__user_id__roadmap_get': unknown;
  // GET /api/v1/organizer/actions  — Get Organizer Actions
  'get_organizer_actions_api_v1_organizer_actions_get': unknown;
  // POST /api/v1/organizer/actions/{action_id}/complete  — Complete Action
  'complete_action_api_v1_organizer_actions__action_id__complete_post': unknown;
  // POST /api/v1/organizer/automation/trigger  — Trigger Automation
  'trigger_automation_api_v1_organizer_automation_trigger_post': unknown;
  // GET /api/v1/organizer/events  — Get Suggested Events
  'get_suggested_events_api_v1_organizer_events_get': unknown;
  // GET /api/v1/users/  — List Users
  'list_users_api_v1_users__get': unknown;
  // GET /api/v1/users/config  — Get Config
  'get_config_api_v1_users_config_get': unknown;
  // POST /api/v1/users/create  — Create User
  'create_user_api_v1_users_create_post': unknown;
  // GET /api/v1/users/{user_id}  — Get User
  'get_user_api_v1_users__user_id__get': unknown;
  // PUT /api/v1/users/{user_id}  — Update User
  'update_user_api_v1_users__user_id__put': unknown;
  // GET /api/v1/users/{user_id}/profile  — Get User Personalization Profile
  'get_user_personalization_profile_api_v1_users__user_id__profile_get': unknown;
  // DELETE /cache/clear  — Clear Cache
  'clear_cache_cache_clear_delete': unknown;
  // GET /health  — Health Check
  'health_check_health_get': unknown;
  // GET /health/agents  — Agents Health
  'agents_health_health_agents_get': unknown;
  // GET /health/cache  — Cache Health
  'cache_health_health_cache_get': unknown;
  // GET /health/llm  — Llm Health
  'llm_health_health_llm_get': unknown;
  // GET /metrics/performance  — Performance Metrics
  'performance_metrics_metrics_performance_get': unknown;
}
