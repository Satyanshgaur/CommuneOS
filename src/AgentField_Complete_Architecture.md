# AgentField.ai: Community Operations Agent
## Complete Technical Architecture & Implementation Guide

**Project Status:** Hackathon-Ready Architecture  
**Target Timeline:** 3-4 weeks (MVP → Polished)  
**Primary Focus:** Dashboard as Product + Agent Reasoning Layer  

---

## Table of Contents
1. [Product Vision](#product-vision)
2. [Core Insight](#core-insight)
3. [System Architecture](#system-architecture)
4. [Data Models](#data-models)
5. [Agent System Design](#agent-system-design)
6. [Implementation Phases](#implementation-phases)
7. [Backend Architecture](#backend-architecture)
8. [Frontend Architecture](#frontend-architecture)
9. [Agent Orchestration](#agent-orchestration)
10. [Deployment Strategy](#deployment-strategy)
11. [Success Metrics & KPIs](#success-metrics--kpis)

---

## Product Vision

### The Problem
Communities with 10,000+ members face information overload:
- New members don't know where to start
- Top contributors aren't being leveraged as mentors
- Valuable events go unattended
- Resources are buried and undiscovered
- Organizers have no operational intelligence

### The Solution
**A personalized, agent-driven dashboard that:**
1. **Understands each member** (Identity Agent) → Profile, goals, skill level, interests
2. **Tracks learning progress** (Learning Agent) → Roadmaps, completed courses, skill gaps
3. **Recommends intelligently** (Discovery Agent) → People, communities, resources, events
4. **Facilitates mentorship** (Mentor Agent) → Matches experts with learners
5. **Provides operational insights** (Organizer Agent) → Health metrics, suggested actions

### The Core Idea
**The dashboard IS the product. Everything else justifies why it looks the way it does.**

---

## Core Insight

**Dashboard Philosophy:**

Instead of passive information display → **Active decision-making**.

| Traditional | AgentField |
|---|---|
| "Here are all channels" | "Here are 3 channels for you, 5 hidden for now" |
| "Recent community posts" | "3 things you should do today" |
| "Online members list" | "Sarah, your ideal CUDA mentor (94% match)" |
| "All uploaded resources" | "CUDA Optimization (matches your workshop tomorrow)" |
| "All upcoming events" | "GPU AMA (aligns with your current learning)" |

**Every card on the dashboard has a "Why?" button that reveals:**
- Which agents evaluated this
- What signals triggered the recommendation
- Confidence score
- Explicit reasoning chain

This transforms the dashboard from "recommendations" → "transparent AI reasoning showcase."

---

## System Architecture

### High-Level Flow

```
User Login
    ↓
Profile Service (Identity Data)
    ↓
Event Stream (User Activity)
    ↓
[Agent Orchestrator]
    ├─ Identity Agent (profile analysis)
    ├─ Learning Agent (skill tracking)
    ├─ Discovery Agent (recommendation)
    ├─ Mentor Agent (matching)
    └─ Organizer Agent (operations)
    ↓
Result Cache (Redis)
    ↓
Dashboard Renderer (Frontend)
    ↓
Reasoning Modal (Explainability)
```

### System Components

```
┌─────────────────────────────────────────────────────┐
│                    Frontend Layer                    │
│  ┌──────────────┬──────────────┬──────────────┐    │
│  │ Member Dash  │ Organizer    │ Agent View   │    │
│  │              │ Dashboard    │              │    │
│  └──────────────┴──────────────┴──────────────┘    │
└──────────────────────┬────────────────────────────┘
                       │
┌──────────────────────┴────────────────────────────┐
│                    API Gateway                     │
│  (Auth, Rate Limiting, Request Routing)           │
└──────────────────────┬────────────────────────────┘
                       │
┌──────────────────────┴────────────────────────────────────────┐
│                   Backend Services                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Agent Orchestrator Service                          │   │
│  │  ├─ Agent Manager (lifecycle)                        │   │
│  │  ├─ Agent Router (task dispatch)                     │   │
│  │  └─ Consensus Engine (result aggregation)            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ Profile      │ Activity     │ Recommendation           │ │
│  │ Service      │ Service      │ Service                  │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
│                                                               │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ Member       │ Resource     │ Event                    │ │
│  │ Service      │ Service      │ Service                  │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└───────────────┬─────────────────────────────────┬──────────┘
                │                                 │
    ┌───────────▼──────────────┐   ┌─────────────▼──────────┐
    │   PostgreSQL (Primary)   │   │   Redis (Cache/Queue)  │
    │   ├─ Users              │   │   ├─ Agent Results     │
    │   ├─ Profiles           │   │   ├─ User Sessions     │
    │   ├─ Activities         │   │   ├─ Recommendation    │
    │   ├─ Resources          │   │   │   Cache            │
    │   ├─ Events             │   │   └─ Job Queue         │
    │   └─ Mentorships        │   │                        │
    └────────────────────────┘   └────────────────────────┘
```

---

## Data Models

### Core Entities

#### User Profile
```
User
├─ id: UUID
├─ email: String
├─ name: String
├─ avatar: String
├─ bio: String
├─ role: ENUM [member, moderator, organizer, admin]
├─ skill_level: ENUM [beginner, intermediate, advanced, expert]
├─ interests: [String] (tags)
├─ goals: [String] (learning objectives)
├─ verified_skills: [Skill]
│  └─ skill: String
│  └─ proficiency: INT [1-5]
│  └─ years_experience: INT
├─ created_at: Timestamp
├─ last_active: Timestamp
└─ metadata: JSON
```

#### Activity Log
```
Activity
├─ id: UUID
├─ user_id: UUID
├─ activity_type: ENUM [viewed, commented, posted, shared, completed, attended, bookmarked]
├─ entity_type: ENUM [resource, event, post, member, community]
├─ entity_id: UUID
├─ timestamp: Timestamp
├─ context: JSON (metadata specific to activity)
├─ duration_seconds: INT (for viewed activities)
└─ engagement_score: FLOAT (computed)
```

#### Learning Path
```
LearningPath
├─ id: UUID
├─ user_id: UUID
├─ skill_name: String
├─ status: ENUM [not_started, in_progress, completed, paused]
├─ progress_percentage: INT [0-100]
├─ milestones: [Milestone]
│  ├─ id: UUID
│  ├─ title: String
│  ├─ description: String
│  ├─ completed: Boolean
│  └─ completed_at: Timestamp
├─ estimated_completion: Timestamp
├─ resources_completed: INT
├─ resources_total: INT
├─ created_at: Timestamp
├─ updated_at: Timestamp
└─ metadata: JSON
```

#### Community/Channel
```
Community
├─ id: UUID
├─ name: String
├─ description: String
├─ icon: String
├─ visibility: ENUM [public, private, hidden]
├─ topics: [String]
├─ member_count: INT
├─ created_at: Timestamp
├─ owner_id: UUID
├─ members: [UUID]
├─ featured: Boolean
└─ metadata: JSON
```

#### Event
```
Event
├─ id: UUID
├─ title: String
├─ description: String
├─ event_type: ENUM [workshop, webinar, ama, meetup, conference]
├─ start_time: Timestamp
├─ end_time: Timestamp
├─ location: String (or URL for virtual)
├─ capacity: INT
├─ registered_count: INT
├─ tags: [String]
├─ organizer_id: UUID
├─ communities: [UUID]
├─ skill_level: ENUM [beginner, intermediate, advanced, any]
├─ created_at: Timestamp
└─ metadata: JSON
```

#### Resource
```
Resource
├─ id: UUID
├─ title: String
├─ description: String
├─ resource_type: ENUM [article, video, book, course, tool, template]
├─ url: String
├─ skill_tags: [String]
├─ difficulty: ENUM [beginner, intermediate, advanced]
├─ estimated_duration_minutes: INT
├─ author_id: UUID
├─ views: INT
├─ bookmarks: INT
├─ created_at: Timestamp
├─ updated_at: Timestamp
└─ metadata: JSON
```

#### Mentorship
```
Mentorship
├─ id: UUID
├─ mentor_id: UUID
├─ mentee_id: UUID
├─ skill_focus: String
├─ status: ENUM [pending, active, completed, declined]
├─ created_at: Timestamp
├─ started_at: Timestamp
├─ ended_at: Timestamp
├─ sessions: INT
├─ notes: String
└─ feedback: JSON
```

#### Agent Decision Log (Critical for Explainability)
```
AgentDecision
├─ id: UUID
├─ decision_id: UUID (groups related decisions)
├─ user_id: UUID
├─ agent_name: ENUM [Identity, Learning, Discovery, Mentor, Organizer]
├─ agent_version: String
├─ decision_type: String (e.g., "recommend_person", "recommend_event")
├─ input_signals: JSON
│  └─ extracted features from user profile/activity
├─ output_results: JSON
│  └─ recommendations with scores
├─ reasoning_chain: JSON
│  └─ step-by-step explanation
├─ confidence_score: FLOAT [0-1]
├─ timestamp: Timestamp
├─ feedback: JSON (user rating if available)
└─ metadata: JSON
```

---

## Agent System Design

### Agent Architecture

Each agent is a **stateless decision-making function** that:
1. Takes **input signals** (user data, activities, profiles)
2. Applies **decision logic** (rules, ML models, heuristics)
3. Returns **ranked recommendations** with reasoning
4. Logs all decisions for explainability

### Agent Specifications

#### 1. Identity Agent
**Purpose:** Profile understanding, skill detection, goal tracking

**Inputs:**
- User profile data
- Verified skills history
- Recent activities
- Self-stated goals

**Logic:**
```
identify_user_profile(user_id) {
  profile = get_user_profile(user_id)
  skills = extract_verified_skills(profile)
  inferred_skills = infer_from_activity(user_id)
  goals = extract_goals(profile)
  maturity_level = calculate_skill_maturity(skills)
  
  return {
    explicit_skills: skills,
    inferred_skills: inferred_skills,
    goals: goals,
    skill_level: maturity_level,
    confidence: calculate_confidence(...)
  }
}
```

**Output:**
- Detected skills (verified + inferred)
- Skill maturity levels
- Current learning objectives
- Career stage classification

**Example Decision Log:**
```json
{
  "agent": "Identity",
  "user": "rahul",
  "reasoning_chain": [
    "CUDA expertise detected: 4 verified skills, 95% match",
    "Linux systems focus: 12 relevant discussions, 8 hours activity",
    "Skill level: Intermediate moving to Advanced",
    "Goals: GPU optimization, ML systems, kernel development"
  ],
  "confidence": 0.94
}
```

---

#### 2. Learning Agent
**Purpose:** Track skill progression, identify gaps, recommend learning paths

**Inputs:**
- User's learning paths
- Completed resources
- Activity on skill-related content
- Goal alignment

**Logic:**
```
analyze_learning_progress(user_id) {
  paths = get_learning_paths(user_id)
  completed_resources = get_completed_resources(user_id)
  skill_gaps = identify_gaps(paths, completed_resources)
  next_milestones = suggest_next_steps(paths)
  momentum = calculate_learning_momentum(user_id)
  
  return {
    active_paths: paths,
    progress_per_path: calculate_progress(...),
    identified_gaps: skill_gaps,
    next_recommended_milestones: next_milestones,
    momentum_score: momentum,
    estimated_completion: estimate_completion_time(...)
  }
}
```

**Output:**
- Current learning paths and progress
- Skill gaps identified
- Recommended next milestones
- Estimated completion timelines
- Learning momentum indicator

**Example Decision Log:**
```json
{
  "agent": "Learning",
  "user": "rahul",
  "reasoning_chain": [
    "CUDA Roadmap: 70% complete (7/10 milestones done)",
    "Current momentum: High (3 completed this week)",
    "Skill gap detected: CUDA Memory Management",
    "Next milestone aligns with GPU Workshop (tomorrow)",
    "Suggests continuing to maintain momentum"
  ],
  "confidence": 0.88
}
```

---

#### 3. Discovery Agent
**Purpose:** Intelligent resource, event, and community recommendations

**Inputs:**
- User profile and interests
- Completed activities
- Community metadata
- Resource/Event metadata
- Temporal relevance

**Logic:**
```
discover_recommendations(user_id) {
  user_profile = get_identity_agent_output(user_id)
  learning_state = get_learning_agent_output(user_id)
  interests = extract_tags(user_profile.interests + inferred_interests)
  skill_level = user_profile.skill_level
  
  resources = rank_resources(
    filter_by_interests(interests),
    filter_by_skill_level(skill_level),
    boost_by_learning_path_alignment(learning_state),
    boost_by_temporal_relevance(user_id),
    decay_by_already_seen(user_id)
  )
  
  events = rank_events(
    filter_by_skill_level(skill_level),
    filter_by_interests(interests),
    filter_by_proximity_to_learning_path(learning_state),
    boost_by_upcoming_timing(...),
    boost_by_expert_availability(...)
  )
  
  communities = rank_communities(
    filter_by_topic_relevance(interests),
    boost_by_learning_alignment(learning_state),
    hide_irrelevant(user_profile),
    sort_by_member_maturity(...)
  )
  
  return {
    top_resources: top_n(resources, 3),
    top_events: top_n(events, 3),
    recommended_communities: top_n(communities, 3),
    reasons: generate_reasons(...)
  }
}
```

**Output:**
- Top 3-5 resources ranked by relevance
- Top 3-5 events with timing context
- Recommended communities (show 3, hide others)
- Explicit reasoning for each recommendation

**Example Decision Log:**
```json
{
  "agent": "Discovery",
  "user": "rahul",
  "resources": [
    {
      "id": "cuda-memory-opt",
      "title": "CUDA Memory Optimization",
      "score": 0.96,
      "reasoning": [
        "Matches CUDA learning path (skill gap detected)",
        "GPU Workshop is tomorrow (temporal boost)",
        "Difficulty: Advanced (matches skill level)"
      ]
    }
  ],
  "events": [
    {
      "id": "gpu-workshop",
      "title": "GPU Systems Workshop",
      "time": "Today 7 PM",
      "score": 0.94,
      "reasoning": [
        "Aligns with active CUDA learning (70% complete)",
        "Expert instructors in GPU systems",
        "Matches current project focus"
      ]
    }
  ],
  "confidence": 0.91
}
```

---

#### 4. Mentor Agent
**Purpose:** Match experts with learners for effective mentorship

**Inputs:**
- Mentee profile, skills, goals
- Mentor profiles, expertise, availability
- Mentorship history
- Success metrics

**Logic:**
```
find_mentor_matches(mentee_id) {
  mentee = get_user_profile(mentee_id)
  mentee_skill_gaps = get_learning_agent_output(mentee_id).skill_gaps
  
  potential_mentors = filter_users(
    skill_level >= mentee.skill_level + 1,
    has_expertise_in(mentee_skill_gaps),
    available_for_mentorship = True,
    mentor_rating >= 4.0
  )
  
  ranked_mentors = rank_by(
    skill_match_score(mentee_skill_gaps, mentor_expertise),
    mentorship_success_rate(mentor),
    communication_compatibility(mentee, mentor),
    availability_overlap(mentee, mentor),
    geographic_proximity_or_timezone(...),
    previous_mentorship_experience(mentee_skill)
  )
  
  return {
    top_matches: top_n(ranked_mentors, 3),
    match_scores: detailed_scores(...),
    reasoning: explain_matches(...)
  }
}
```

**Output:**
- Top 3 mentor matches with compatibility scores
- Specific skill alignment explanations
- Success rate indicators
- One-click connection option

**Example Decision Log:**
```json
{
  "agent": "Mentor",
  "user": "rahul",
  "matches": [
    {
      "mentor": "sarah",
      "title": "CUDA Engineer",
      "score": 0.94,
      "reasoning": [
        "Expert in CUDA (5 years, mentored 12 others)",
        "Helps beginners (Rahul is intermediate)",
        "Active in community (high mentor rating)",
        "Available for 1:1 sessions"
      ]
    }
  ],
  "confidence": 0.94
}
```

---

#### 5. Organizer Agent
**Purpose:** Provide operational intelligence and suggested actions

**Inputs:**
- Entire community health metrics
- Member activity trends
- Unanswered questions
- Potential growth opportunities

**Logic:**
```
analyze_community_health() {
  metrics = {
    new_members: count_joined_this_period(...),
    active_members: count_active_this_period(...),
    at_risk_members: detect_churn_signals(...),
    trending_topics: extract_trending_topics(...),
    unanswered_questions: find_unanswered(...),
    mentor_availability: evaluate_mentor_pool(...),
    event_success_rate: calculate_event_metrics(...),
    resource_discovery_rate: measure_resource_usage(...)
  }
  
  suggested_actions = generate_actions(metrics)
  
  return {
    health_metrics: metrics,
    suggested_actions: suggested_actions,
    priority_level: calculate_priority(...),
    impact_estimate: estimate_impact(...)
  }
}
```

**Output:**
- Community health scorecard
- Suggested operational actions
- At-risk members needing attention
- Content gaps to fill

**Example Decision Log:**
```json
{
  "agent": "Organizer",
  "community": "entire_community",
  "insights": [
    {
      "metric": "unanswered_questions",
      "value": 12,
      "severity": "medium",
      "suggestion": "Create FAQ or schedule AMA",
      "assign_to": "sarah"
    },
    {
      "metric": "potential_mentors",
      "value": 3,
      "action": "Suggest mentorship program to: Rahul, Sarah, Aman",
      "impact": "Could help 15+ beginners"
    }
  ]
}
```

---

### Agent Orchestration

#### Orchestrator Service
```
AgentOrchestrator {
  
  async function execute_dashboard_request(user_id, context) {
    // Run agents in parallel
    const [identity, learning, discovery, mentor] = await Promise.all([
      IdentityAgent.analyze(user_id),
      LearningAgent.analyze(user_id),
      DiscoveryAgent.analyze(user_id),
      MentorAgent.analyze(user_id)
    ])
    
    // Aggregate results
    const dashboard_data = {
      user: identity,
      priorities: extract_priorities(identity, learning),
      recommended_people: mentor.top_matches,
      communities_for_you: discovery.communities,
      recommended_resources: discovery.resources,
      upcoming_events: discovery.events,
      insights: generate_insights(identity, learning)
    }
    
    // Cache for 15 minutes
    cache.set(`dashboard:${user_id}`, dashboard_data, 900)
    
    // Log all decisions for explainability
    log_agent_decisions({
      user_id,
      identity, learning, discovery, mentor,
      timestamp: now()
    })
    
    return dashboard_data
  }
  
  async function execute_organizer_request(community_id) {
    const organizer_insights = await OrganizerAgent.analyze(community_id)
    cache.set(`org_dashboard:${community_id}`, organizer_insights, 600)
    return organizer_insights
  }
}
```

---

## Implementation Phases

### Phase 1: Core Foundation (Week 1-2)
**Goal:** Working dashboard with mock data and basic agent logic

#### Phase 1A: Data Layer
```
Tasks:
□ PostgreSQL schema design & migrations
  ├─ Users table
  ├─ Activities table
  ├─ Learning paths table
  ├─ Resources table
  ├─ Events table
  ├─ Communities table
  └─ Agent decisions table
□ Redis setup & cache key design
□ Seed database with mock profiles (5-10 users)
□ Create sample data: resources, events, communities
□ Write data access layers (DAL)

Deliverable:
- PostgreSQL with full schema
- Redis cache operational
- 10 realistic user profiles
- 50+ resources, 15+ events
```

#### Phase 1B: Backend API Foundation
```
Tasks:
□ Set up API framework (Express.js or Go)
□ Create core endpoints:
  ├─ GET /api/users/:id (profile)
  ├─ GET /api/dashboard/:id (main dashboard)
  ├─ GET /api/organizer/dashboard (org view)
  └─ GET /api/decisions/:id (explainability)
□ Implement authentication (JWT)
□ Add rate limiting
□ Error handling & logging

Deliverable:
- API running on localhost:3000
- All core endpoints working
- Mock data flowing through
```

#### Phase 1C: Simple Agent Implementation
```
Tasks:
□ Identity Agent (basic)
  └─ Returns: user skills, skill level
□ Learning Agent (basic)
  └─ Returns: current paths, progress %
□ Discovery Agent (basic)
  └─ Returns: top 3 resources, events, communities
□ Mentor Agent (basic)
  └─ Returns: top 3 mentor matches
□ All agents return static reasoning

Deliverable:
- All 5 agents runnable
- Return data in correct format
- Agent decision logging working
```

#### Phase 1D: Frontend Foundation
```
Tasks:
□ Set up React project
□ Create dashboard layout (sections structure)
□ Create role switcher (Member view → Organizer view)
□ Add mock API integration
□ Basic styling (dark theme starter)

Deliverable:
- Dashboard renders with mock data
- Role switching works
- Basic styling applied
```

#### Phase 1E: Explainability Modal
```
Tasks:
□ Create "Why?" modal component
□ Parse agent decision logs
□ Display reasoning chain
□ Show confidence scores
□ Show input signals

Deliverable:
- Click any card → see agent reasoning
- Clean modal UI
- Clear explanation text
```

**Phase 1 Checkpoint Deliverable:**
- A working dashboard displaying personalized cards
- Click role switcher → dashboard changes for different users
- Click "Why?" → see agent reasoning
- **Demo time: 60 seconds of switching roles and clicking explanations**

---

### Phase 2: Enhanced Agents & Intelligence (Week 2-3)
**Goal:** Replace mock logic with real decision-making

#### Phase 2A: Learning Agent Enhancement
```
Tasks:
□ Implement learning path progression tracking
□ Calculate skill gaps from activities
□ Prioritize learning goals
□ Estimate completion times
□ Track momentum (frequency of learning activity)

Logic to Add:
- Parse user activity for skill learning signals
- Weight recent activities higher than old
- Detect learning patterns (consistent vs sporadic)
- Identify bottleneck skills
- Suggest next logical milestones

Deliverable:
- Learning paths show actual progress
- "Finish CUDA Roadmap" card has real 70% progress
- Completion estimates are calculated
```

#### Phase 2B: Discovery Agent Enhancement
```
Tasks:
□ Implement relevance scoring:
  ├─ Interest tag matching
  ├─ Skill level filtering
  ├─ Temporal proximity (upcoming vs far events)
  ├─ Learning path alignment
  └─ Already-seen decay
□ Implement resource ranking
□ Implement event ranking
□ Implement community hiding logic

Scoring Algorithm (Example):
```
resource_score = (
  interest_match * 0.3 +
  skill_level_alignment * 0.3 +
  learning_path_alignment * 0.2 +
  recency_boost * 0.1 +
  popularity_signal * 0.1
) * already_seen_decay
```

Deliverable:
- Resources ranked by real relevance
- Events show upcoming, not all
- Communities show 3-5, hide others
```

#### Phase 2C: Mentor Agent Enhancement
```
Tasks:
□ Implement skill compatibility matching
□ Factor in mentorship availability
□ Calculate mentorship success rates
□ Weight by mentor communication style
□ Consider timezone/geographic proximity
□ Pull actual mentor profiles

Matching Algorithm:
```
mentor_score = (
  skill_match * 0.35 +
  success_rate * 0.25 +
  availability * 0.2 +
  communication_fit * 0.1 +
  previous_experience * 0.1
)
```

Deliverable:
- Real mentor matches based on skills
- Confidence scores 80%+
- Reasoning shows skill gaps vs mentor expertise
```

#### Phase 2D: Organizer Agent
```
Tasks:
□ Community health scoring
□ Trending topics extraction
□ At-risk member detection
□ Suggested action generation
□ Impact estimation

Metrics to Track:
- New members (past week)
- Churn risk (no activity > 30 days)
- Engagement rate (active members %)
- Question answer rate
- Event attendance rate
- Mentor availability

Deliverable:
- Organizer dashboard shows real metrics
- Suggested actions are data-driven
- Health score visible
```

#### Phase 2E: Reasoning Enhancement
```
Tasks:
□ Improve explanation chains
□ Add signal visualization in modal
□ Show which factors contributed most
□ Display confidence breakdown
□ Add "How can I improve this recommendation?" hints

Deliverable:
- Explainability modals show actual reasoning
- Clear attribution of signals
- User can understand why
```

**Phase 2 Checkpoint Deliverable:**
- Dashboard powered by real agent logic, not mocks
- Switching users shows dramatically different dashboards
- Reasoning modals show actual decision factors
- **Demo time: Show 3 different users (beginner, intermediate, organizer) with completely different dashboards**

---

### Phase 3: Polish & Explainability (Week 3-4)
**Goal:** Hackathon-ready, showstopping product

#### Phase 3A: Visual Polish
```
Tasks:
□ Refine typography & spacing
□ Optimize card layouts
□ Add micro-interactions
  ├─ Hover effects
  ├─ Smooth transitions
  ├─ Loading states
□ Implement dark theme consistently
□ Add profile images/avatars
□ Color-code agent types
□ Add confidence score visualizations

Design Elements:
- Orange accent (#E8472A or similar)
- Near-black background
- Clean, spacious layout
- Clear visual hierarchy
```

#### Phase 3B: Agent View
```
Tasks:
□ Create detailed agent flow visualization
□ Show: Event trigger → Agent → Decision → Result
□ Display agent sequence diagram
□ Timeline of agent execution
□ Data flow visualization

Visual Example:
```
User Joined
  ↓ [1ms]
Identity Agent (Profile Analysis)
  ├─ Input: User registration form
  ├─ Process: Extract skills, interests, goals
  └─ Output: User identity
  ↓ [5ms]
Discovery Agent (Resource Discovery)
  ├─ Input: User identity
  ├─ Process: Rank resources by relevance
  └─ Output: Top 5 resources
  ↓ [8ms]
Mentor Agent (Expert Matching)
  ├─ Input: User skills, goals
  ├─ Process: Find compatible mentors
  └─ Output: Top 3 mentors
  ↓ [3ms]
Dashboard Refreshed ✓
```

Deliverable:
- Dedicated "How Agents Work" page
- Visual flow diagram
- Proof of multi-agent orchestration
```

#### Phase 3C: Data-Driven Reasoning Chains
```
Tasks:
□ For each recommendation card, add data citations:
  
  Example Before:
  "GPU Systems Workshop - Recommended"
  
  Example After:
  "GPU Systems Workshop - Recommended because you've 
   completed 70% of the CUDA learning path (7/10 
   milestones) and interacted with 3 GPU discussions 
   this week. Expert: Dr. Patel (4.8★, mentored 25+ 
   engineers). Event: Today 7 PM, capacity 30/30."

□ Add signal breakdown:
  ├─ Primary: Learning path alignment (96%)
  ├─ Secondary: Interest match (94%)
  ├─ Temporal: Today, optimal timing (88%)
  └─ Meta: Similar learners attending (82%)

Deliverable:
- Every card shows reasoning
- Judges see transparent AI decision-making
```

#### Phase 3D: Organizer Intelligence
```
Tasks:
□ Real-time community health metrics
□ Suggested actions with impact estimates:
  ├─ "Schedule GPU AMA - could help 8 members"
  ├─ "Assign Sarah as mentor - matches 5 learners"
  ├─ "Create CUDA FAQ - answers 12 pending questions"
□ Member at-risk flags
□ Trending topics heatmap
□ Growth projections

Deliverable:
- Organizer dashboard is actionable intelligence
- Every suggestion has impact number
```

#### Phase 3E: Edge Cases & Performance
```
Tasks:
□ Handle cold-start (new users):
  ├─ Recommend by demographics
  ├─ Show popular resources
  ├─ Suggest onboarding mentors
□ Cache strategies:
  ├─ Dashboard: 15 min
  ├─ User profile: 5 min
  ├─ Discovery results: 30 min
  └─ Organizer metrics: 10 min
□ Load testing:
  ├─ Target: 100+ concurrent users
  └─ Dashboard load: <500ms
□ Error handling & graceful degradation

Deliverable:
- Fast, reliable product
- Handles edge cases
```

#### Phase 3F: Demo Sequence
```
Prepare Perfect Demo (45 seconds):

[0s] "This is a 10,000-member community."
[2s] Click Rahul (GPU engineer)
     → Dashboard shows systems-focused, everything CUDA
[8s] Click Priya (beginner)
     → Dashboard completely different, beginner-friendly
[14s] Click Organizer
     → Dashboard becomes operational intelligence
[20s] Click "Why am I seeing this?" on GPU Workshop
     → Modal shows: Identity → Learning → Discovery
     → Shows reasoning: learning path, skill level, timing
     → Shows confidence: 96%
[35s] "Every card is transparent AI reasoning. 
      Click any card to understand why it's there."
[40s] Show agent view: "Multiple agents collaborated
      to create this personalized experience."
[45s] End
```

**Phase 3 Checkpoint Deliverable:**
- Production-grade UI/UX
- Explainability is the hero
- Agent view proves multi-agent orchestration
- Perfect 45-second demo sequence
- **Ready for competition**

---

## Backend Architecture

### Technology Stack

```
Language: Go or Node.js
Framework: Gin (Go) or Express.js (Node)
Database: PostgreSQL 14+
Cache: Redis 6+
Queue: Redis Streams or Bull.js
Logging: Winston/Morgan + ELK (optional)
Authentication: JWT + bcrypt
Deployment: Docker + Docker Compose
```

### Service Structure

```
agentfield/
├─ cmd/
│  ├─ api/
│  │  └─ main.go (API server startup)
│  └─ worker/
│     └─ main.go (background job processor)
├─ internal/
│  ├─ handlers/
│  │  ├─ dashboard.go
│  │  ├─ user.go
│  │  ├─ organizer.go
│  │  └─ decisions.go
│  ├─ services/
│  │  ├─ identity_agent.go
│  │  ├─ learning_agent.go
│  │  ├─ discovery_agent.go
│  │  ├─ mentor_agent.go
│  │  ├─ organizer_agent.go
│  │  ├─ orchestrator.go
│  │  └─ cache.go
│  ├─ models/
│  │  ├─ user.go
│  │  ├─ activity.go
│  │  ├─ resource.go
│  │  ├─ event.go
│  │  ├─ learning_path.go
│  │  └─ agent_decision.go
│  ├─ repository/
│  │  ├─ user_repo.go
│  │  ├─ activity_repo.go
│  │  ├─ resource_repo.go
│  │  ├─ event_repo.go
│  │  ├─ decision_repo.go
│  │  └─ db.go
│  ├─ middleware/
│  │  ├─ auth.go
│  │  ├─ logger.go
│  │  └─ rate_limit.go
│  └─ utils/
│     ├─ scoring.go
│     ├─ ranking.go
│     └─ helpers.go
├─ pkg/
│  ├─ config/
│  │  └─ config.go
│  └─ errors/
│     └─ errors.go
├─ migrations/
│  ├─ 001_initial_schema.up.sql
│  ├─ 001_initial_schema.down.sql
│  └─ ...
├─ docker-compose.yml
├─ Dockerfile
├─ go.mod
└─ README.md
```

### API Endpoints

#### User Dashboard
```
GET /api/v1/dashboard
Headers: Authorization: Bearer {token}

Response:
{
  "user": {
    "id": "uuid",
    "name": "Rahul",
    "skill_level": "intermediate",
    "verified_skills": [...]
  },
  "priorities": [
    {
      "id": "event-1",
      "type": "event",
      "title": "GPU Systems Workshop",
      "time": "Today 7 PM",
      "impact_reason": "Helps internship goal"
    },
    ...
  ],
  "recommended_people": [
    {
      "id": "user-2",
      "name": "Sarah",
      "title": "CUDA Engineer",
      "match_score": 0.94,
      "skills": ["CUDA", "GPU"]
    },
    ...
  ],
  "communities_for_you": {
    "show": ["Systems Programming", "AI Infrastructure"],
    "hide": ["Web3", "Anime", "Football"]
  },
  "recommended_resources": [
    {
      "id": "resource-1",
      "title": "CUDA Memory Optimization",
      "difficulty": "intermediate",
      "estimated_duration_minutes": 45
    },
    ...
  ],
  "upcoming_events": [...],
  "insights": [
    {
      "message": "You're among the top 15% contributors this week",
      "data_point": 15,
      "unit": "percentile"
    },
    ...
  ]
}
```

#### Organizer Dashboard
```
GET /api/v1/organizer/dashboard
Headers: Authorization: Bearer {token}

Response:
{
  "community_health": {
    "score": 78,
    "new_members": 38,
    "active_members": 234,
    "at_risk_members": 5,
    "trending_topics": ["CUDA", "Rust", "MCP"],
    "unanswered_questions": 12
  },
  "suggested_actions": [
    {
      "action": "Schedule GPU AMA",
      "reason": "12 unanswered GPU questions",
      "impact": "Could help 8+ members",
      "assign_to": "sarah"
    },
    ...
  ],
  "potential_mentors": [
    {
      "id": "user-1",
      "name": "Rahul",
      "expertise": ["CUDA", "Linux"],
      "could_help": 5
    },
    ...
  ]
}
```

#### Decision Explainability
```
GET /api/v1/decisions/{decision_id}
Headers: Authorization: Bearer {token}

Response:
{
  "decision_id": "dec-1",
  "agents_involved": ["Identity", "Learning", "Discovery"],
  "timeline": [
    {
      "agent": "Identity",
      "duration_ms": 1,
      "inputs": {"skills": ["CUDA"], "goals": [...]},
      "outputs": {"skill_level": "intermediate"}
    },
    ...
  ],
  "final_recommendation": "GPU Systems Workshop",
  "reasoning_chain": [
    "User identified as intermediate CUDA engineer",
    "70% complete CUDA learning path detected",
    "Workshop aligns with learning path (96% match)",
    "Event is happening today (temporal boost)",
    "Expert available: Dr. Patel"
  ],
  "confidence": {
    "overall": 0.94,
    "breakdown": {
      "learning_alignment": 0.96,
      "interest_match": 0.94,
      "temporal_fit": 0.88
    }
  }
}
```

### Core Agent Implementation Example (Go)

```go
// services/discovery_agent.go

type DiscoveryAgent struct {
  resourceRepo *repository.ResourceRepository
  eventRepo    *repository.EventRepository
  activityRepo *repository.ActivityRepository
  cache        *cache.Cache
}

type DiscoveryResult struct {
  Resources []RankedResource
  Events    []RankedEvent
  Communities []RankedCommunity
  Reasoning map[string]interface{}
}

func (da *DiscoveryAgent) Analyze(userID string) (*DiscoveryResult, error) {
  // Get user profile from Identity Agent
  identity, err := identityAgent.Analyze(userID)
  if err != nil {
    return nil, err
  }
  
  // Get learning state from Learning Agent
  learning, err := learningAgent.Analyze(userID)
  if err != nil {
    return nil, err
  }
  
  // Get user activities
  activities, err := da.activityRepo.GetUserActivities(userID, 7)
  if err != nil {
    return nil, err
  }
  
  // Extract interests and seen items
  interests := extractInterests(identity, activities)
  seenResources := extractSeenItems(activities, "resource")
  
  // Rank resources
  resources, err := da.rankResources(
    identity.SkillLevel,
    interests,
    learning.ActivePaths,
    seenResources,
  )
  if err != nil {
    return nil, err
  }
  
  // Rank events
  events, err := da.rankEvents(
    identity.SkillLevel,
    interests,
    learning.ActivePaths,
  )
  if err != nil {
    return nil, err
  }
  
  // Rank communities
  communities, err := da.rankCommunities(
    interests,
    learning.ActivePaths,
    identity.SkillLevel,
  )
  if err != nil {
    return nil, err
  }
  
  return &DiscoveryResult{
    Resources: resources[:3],
    Events: events[:3],
    Communities: communities[:5],
    Reasoning: da.generateReasoning(...),
  }, nil
}

func (da *DiscoveryAgent) rankResources(
  skillLevel string,
  interests []string,
  learningPaths []models.LearningPath,
  seenResources map[string]bool,
) ([]RankedResource, error) {
  
  resources, err := da.resourceRepo.GetAll()
  if err != nil {
    return nil, err
  }
  
  var ranked []RankedResource
  
  for _, r := range resources {
    if seenResources[r.ID] {
      continue // Filter out already seen
    }
    
    score := 0.0
    
    // Interest match (30%)
    interestMatch := calculateTagMatch(r.SkillTags, interests)
    score += interestMatch * 0.3
    
    // Skill level alignment (30%)
    skillMatch := calculateSkillAlignment(r.Difficulty, skillLevel)
    score += skillMatch * 0.3
    
    // Learning path alignment (20%)
    pathMatch := calculatePathAlignment(r.SkillTags, learningPaths)
    score += pathMatch * 0.2
    
    // Temporal relevance (10%)
    // Boost if just added or trending
    temporalBoost := calculateTemporalBoost(r.CreatedAt, r.Views)
    score += temporalBoost * 0.1
    
    // Popularity (10%)
    popularityScore := min(float64(r.Bookmarks) / 100.0, 1.0)
    score += popularityScore * 0.1
    
    ranked = append(ranked, RankedResource{
      Resource: r,
      Score: score,
    })
  }
  
  // Sort by score
  sort.Slice(ranked, func(i, j int) bool {
    return ranked[i].Score > ranked[j].Score
  })
  
  return ranked, nil
}
```

---

## Frontend Architecture

### Technology Stack
```
Framework: React 18+
Build: Vite
State: Context API or Redux
HTTP: Axios
Styling: Tailwind CSS
UI Components: Custom or shadcn/ui
Charts: Recharts (for analytics)
Icons: Feather Icons or Heroicons
Deployment: Vercel or Netlify
```

### Component Structure

```
src/
├─ components/
│  ├─ Dashboard/
│  │  ├─ Dashboard.jsx (main container)
│  │  ├─ PrioritiesSection.jsx
│  │  ├─ PeopleSection.jsx
│  │  ├─ CommunitiesSection.jsx
│  │  ├─ ResourcesSection.jsx
│  │  ├─ EventsSection.jsx
│  │  └─ InsightsSection.jsx
│  ├─ Common/
│  │  ├─ Card.jsx
│  │  ├─ Modal.jsx
│  │  ├─ ExplainabilityModal.jsx
│  │  ├─ Header.jsx
│  │  ├─ RoleSelector.jsx
│  │  └─ LoadingState.jsx
│  ├─ OrganizerDashboard/
│  │  ├─ OrganizerDashboard.jsx
│  │  ├─ HealthMetrics.jsx
│  │  ├─ SuggestedActions.jsx
│  │  └─ MentorPool.jsx
│  └─ AgentView/
│     ├─ AgentView.jsx
│     ├─ AgentTimeline.jsx
│     ├─ AgentFlow.jsx
│     └─ DecisionBreakdown.jsx
├─ pages/
│  ├─ Dashboard.jsx
│  ├─ OrganizerDashboard.jsx
│  ├─ AgentView.jsx
│  └─ Settings.jsx
├─ hooks/
│  ├─ useDashboard.js
│  ├─ useFetch.js
│  └─ useAuth.js
├─ services/
│  ├─ api.js (axios instance)
│  ├─ dashboardService.js
│  ├─ userService.js
│  └─ decisionService.js
├─ context/
│  ├─ AuthContext.jsx
│  └─ DashboardContext.jsx
├─ utils/
│  ├─ formatting.js
│  └─ calculations.js
├─ styles/
│  ├─ globals.css
│  └─ tailwind.config.js
└─ App.jsx
```

### Key Components

#### Dashboard Container
```jsx
export function Dashboard() {
  const { user, dashboardData, loading } = useDashboard()
  const [selectedRole, setSelectedRole] = useState('member')
  
  if (loading) return <LoadingState />
  
  return (
    <div className="min-h-screen bg-zinc-950 text-white">
      <Header user={user} />
      
      <div className="max-w-7xl mx-auto p-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold">
            Welcome back {user.name} 👋
          </h1>
          <RoleSelector 
            current={selectedRole} 
            onChange={setSelectedRole}
          />
        </div>
        
        {selectedRole === 'member' ? (
          <>
            <PrioritiesSection data={dashboardData.priorities} />
            <PeopleSection data={dashboardData.recommended_people} />
            <CommunitiesSection data={dashboardData.communities_for_you} />
            <ResourcesSection data={dashboardData.recommended_resources} />
            <EventsSection data={dashboardData.upcoming_events} />
            <InsightsSection data={dashboardData.insights} />
          </>
        ) : (
          <OrganizerDashboard data={dashboardData.organizer} />
        )}
      </div>
    </div>
  )
}
```

#### Explainability Modal
```jsx
export function ExplainabilityModal({ decision, onClose }) {
  const [expandedAgent, setExpandedAgent] = useState(null)
  
  return (
    <Modal onClose={onClose}>
      <div className="max-w-2xl">
        <h2 className="text-2xl font-bold mb-4">
          Why am I seeing this?
        </h2>
        
        <div className="mb-6">
          <p className="text-gray-300 mb-4">
            Multiple AI agents collaborated to recommend this.
          </p>
          
          <div className="space-y-3">
            {decision.agents_involved.map((agent) => (
              <div
                key={agent}
                className="border border-gray-700 p-4 cursor-pointer
                           hover:border-orange-500 transition"
                onClick={() => setExpandedAgent(
                  expandedAgent === agent ? null : agent
                )}
              >
                <div className="flex justify-between">
                  <span className="font-semibold">{agent} Agent</span>
                  <span className="text-orange-500">
                    {decision.confidence[agent] || '—'}
                  </span>
                </div>
                
                {expandedAgent === agent && (
                  <div className="mt-3 pt-3 border-t border-gray-700">
                    <p className="text-sm text-gray-400">
                      {decision.reasoning_chains[agent]}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
        
        <div className="bg-gray-900 p-4 rounded">
          <p className="text-sm text-gray-400">
            <strong>Overall Confidence:</strong> {decision.confidence_overall}%
          </p>
        </div>
      </div>
    </Modal>
  )
}
```

---

## Agent Orchestration

### Request Flow

```
1. User requests dashboard
   ↓
2. API receives GET /api/v1/dashboard?user_id={id}
   ↓
3. Check Redis cache (key: dashboard:{user_id})
   ├─ Cache hit → return cached data
   └─ Cache miss → proceed to step 4
   ↓
4. Orchestrator.ExecuteDashboardRequest(user_id)
   ↓
5. Parallel execution of 4 agents:
   ├─ go IdentityAgent.Analyze(user_id)
   ├─ go LearningAgent.Analyze(user_id)
   ├─ go DiscoveryAgent.Analyze(user_id)
   └─ go MentorAgent.Analyze(user_id)
   ↓
6. Wait for all agents (max timeout: 2 seconds)
   ↓
7. Aggregate results:
   {
     priorities: extract from Identity + Learning,
     recommended_people: from Mentor,
     communities: from Discovery,
     resources: from Discovery,
     events: from Discovery,
     insights: computed from all
   }
   ↓
8. Log all decisions to AgentDecisions table
   ↓
9. Cache result for 15 minutes
   ↓
10. Return to frontend
    ↓
11. Frontend renders dashboard with decision IDs
    ↓
12. User clicks "Why?" button
    ↓
13. API GET /api/v1/decisions/{decision_id}
    ↓
14. Return full reasoning chain + agent timeline
    ↓
15. Explainability modal renders
```

### Concurrency & Performance

```go
// Parallel Agent Execution with Timeout
func (orch *Orchestrator) ExecuteDashboardRequest(
  ctx context.Context,
  userID string,
) (*DashboardResponse, error) {
  
  // Create buffered channels
  identityChan := make(chan *IdentityResult, 1)
  learningChan := make(chan *LearningResult, 1)
  discoveryChan := make(chan *DiscoveryResult, 1)
  mentorChan := make(chan *MentorResult, 1)
  
  // Set timeout
  ctx, cancel := context.WithTimeout(ctx, 2*time.Second)
  defer cancel()
  
  // Execute agents in parallel
  go func() {
    result, _ := orch.identityAgent.Analyze(userID)
    identityChan <- result
  }()
  
  go func() {
    result, _ := orch.learningAgent.Analyze(userID)
    learningChan <- result
  }()
  
  go func() {
    result, _ := orch.discoveryAgent.Analyze(userID)
    discoveryChan <- result
  }()
  
  go func() {
    result, _ := orch.mentorAgent.Analyze(userID)
    mentorChan <- result
  }()
  
  // Collect results with timeout handling
  identity := <-identityChan
  learning := <-learningChan
  discovery := <-discoveryChan
  mentor := <-mentorChan
  
  // Aggregate and format response
  response := orch.aggregateResults(
    identity, learning, discovery, mentor,
  )
  
  // Log decisions for explainability
  orch.logDecisions(userID, identity, learning, discovery, mentor)
  
  // Cache result
  orch.cache.Set(
    fmt.Sprintf("dashboard:%s", userID),
    response,
    15*time.Minute,
  )
  
  return response, nil
}
```

---

## Deployment Strategy

### Development Environment

```bash
# Docker Compose for local development
docker-compose up

# Services:
# - API: http://localhost:3000
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: agentfield
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: agentfield
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://agentfield:dev_password@postgres:5432/agentfield
      REDIS_URL: redis://redis:6379
      JWT_SECRET: dev_secret_key
      NODE_ENV: development
    depends_on:
      - postgres
      - redis
    volumes:
      - .:/app

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      VITE_API_URL: http://localhost:3000
    depends_on:
      - api

volumes:
  postgres_data:
```

### Production Deployment

```
Frontend:
- Build: npm run build
- Deploy to: Vercel / Netlify
- Domain: agentfield.ai

Backend:
- Build Docker image
- Push to Docker Hub
- Deploy to: AWS ECS / Railway / Render
- Database: AWS RDS PostgreSQL
- Cache: AWS ElastiCache Redis
- CDN: CloudFront

Environment Variables:
- DATABASE_URL: prod postgres connection
- REDIS_URL: prod redis connection
- JWT_SECRET: secure random key
- API_PORT: 3000
- NODE_ENV: production
```

---

## Success Metrics & KPIs

### For Competition Judges

1. **Dashboard Clarity**: Users understand their personalized recommendations immediately
2. **Agent Transparency**: "Why?" button proves AI reasoning is explainable
3. **Role Switching Impact**: Switching users creates visibly different dashboards
4. **Organizer Intelligence**: Operations view shows AI beyond personal recommendations
5. **Multi-Agent Proof**: Agent view clearly shows collaboration between agents

### Technical Metrics

```
Performance:
- Dashboard load time: < 500ms
- Agent response time: < 2s (parallel)
- Cache hit rate: > 80%
- API uptime: > 99%

Scalability:
- Support 100+ concurrent users
- Queries per second: > 1000
- Database connections: pooled to 20

Quality:
- Code coverage: > 80%
- Test passing: 100%
- Type safety: TypeScript/Go
```

### Business Metrics

```
Engagement:
- Users clicking "Why?" per session: target 3+
- Dashboard refresh frequency: ~every 15 min
- Time spent on platform: > 10 min/session
- Click-through on recommendations: > 30%

Retention:
- Mentor connections made: track for real communities
- Event attendance from recommendations
- Resource completion rate
- Learning path progression
```

---

## Advanced Features (Post-MVP)

### Phase 4: Machine Learning Integration
```
□ Implement real collaborative filtering
□ Build user embedding space (skills, interests)
□ Isolation Forest for anomaly detection
□ Natural language processing for resource descriptions
□ Computer vision for event/profile image understanding
```

### Phase 5: Real Integration
```
□ Discord API integration
□ Slack notifications
□ Calendar integration (Google Calendar, Outlook)
□ Email digest system
□ Push notifications
```

### Phase 6: Analytics & Feedback Loop
```
□ Recommendation feedback collection
□ A/B testing framework
□ Agent performance tracking
□ User satisfaction surveys
□ Continuous agent improvement
```

---

## Summary

**AgentField.ai is fundamentally a dashboard-driven product** where:

1. **The dashboard is the hero** — Personalized cards powered by AI agents
2. **Explainability is the magic** — Users can click "Why?" to see agent reasoning
3. **Multi-agent orchestration is proven** — Agent view shows collaboration
4. **Role switching demonstrates power** — Same community, completely different views

**Key Implementation Strategy:**

- **Phase 1 (Weeks 1-2):** Working dashboard with mock agents
- **Phase 2 (Weeks 2-3):** Real agent logic and intelligence
- **Phase 3 (Weeks 3-4):** Polish, explainability, demo perfection

**Why This Wins Hackathons:**

- Clear problem (community info overload)
- Elegant solution (AI-powered personalization)
- Transparent AI (explainability modals)
- Scalable architecture (agent-based)
- Impressive demo (45-second role-switch showcase)

**Build it. You've got this.** 🚀

---

## Appendix: Quick Reference

### Core Files to Create (Priority Order)

1. **Database Schema** → `migrations/001_initial.sql`
2. **Models** → `internal/models/`
3. **Repositories** → `internal/repository/`
4. **Agents** → `internal/services/*_agent.go`
5. **Orchestrator** → `internal/services/orchestrator.go`
6. **Handlers** → `internal/handlers/`
7. **Frontend Components** → `src/components/Dashboard/`
8. **Explainability Modal** → `src/components/ExplainabilityModal.jsx`

### Environment Setup Checklist

- [ ] PostgreSQL installed and running
- [ ] Redis installed and running
- [ ] Go 1.20+ or Node.js 18+
- [ ] React project scaffolded
- [ ] Docker and Docker Compose installed
- [ ] git initialized and tracked
- [ ] .env files configured
- [ ] Database migrations applied

### Demo Checklist

- [ ] 3 different user profiles in database
- [ ] Dashboard loads in < 500ms
- [ ] Role switcher changes everything
- [ ] "Why?" modals show real reasoning
- [ ] Organizer view shows operations
- [ ] Agent view shows collaboration timeline
- [ ] No console errors or warnings
- [ ] Mobile responsive (if judged on mobile)

---

**Last Updated:** June 2026  
**Status:** Ready for implementation  
**Estimated Complexity:** High (suitable for hackathon track 2)
