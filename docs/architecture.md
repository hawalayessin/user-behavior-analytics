# User Analytics Platform - Architecture Diagram

## System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        User["👤 End User"]
    end
    
    subgraph "Frontend Application"
        Browser["🌐 Web Browser"]
        React["React 19.2.0<br/>- Pages: Dashboard, Auth, Users<br/>- Components: Charts, Tables, Forms"]
        Vite["Vite 7.3.1<br/>Build & Dev Server"]
        Router["React Router<br/>Protected Routes"]
        AxiosClient["Axios HTTP Client<br/>+ JWT Interceptor"]
    end
    
    subgraph "Backend Application"
        FastAPI["FastAPI Server<br/>Port: 8000"]
        AuthRouter["Auth Router<br/>/auth"]
        UsersRouter["Users Router<br/>/users"]
        PlatformRouter["Platform Users<br/>/platform-users"]
        AnalyticsRouter["Analytics Router<br/>/analytics"]
        ActivityRouter["Activity Router<br/>/user-activity"]
        ServiceRouter["Service Router<br/>/service"]
        Security["Security Layer<br/>JWT, Bcrypt, CORS"]
        SQLAlchemy["SQLAlchemy ORM<br/>Data Layer"]
    end
    
    subgraph "Data Models"
        Users["👥 Users"]
        PlatformUsers["🔧 Platform Users"]
        Campaigns["📢 Campaigns"]
        Events["📊 Events"]
        Subscriptions["📋 Subscriptions"]
        Activities["📈 Activities"]
        Services["⚙️ Services"]
    end
    
    subgraph "Database Layer"
        PostgreSQL["PostgreSQL 15<br/>analytics_db"]
        Alembic["Alembic<br/>Migrations"]
        Storage["postgres_data Volume<br/>Persistent Storage"]
    end
    
    subgraph "Infrastructure"
        Docker["🐳 Docker Compose"]
        FrontendContainer["Frontend Container<br/>Port: 5173"]
        BackendContainer["Backend Container<br/>Port: 8000"]
        DBContainer["DB Container<br/>Port: 5432"]
    end
    
    %% User interactions
    User -->|Accesses| Browser
    Browser -->|Renders| React
    React -->|Routes| Router
    
    %% Frontend to Backend
    Router -->|Protected Routes| React
    React -->|HTTP REST<br/>+ JWT Token| AxiosClient
    AxiosClient -->|API Requests| FastAPI
    
    %% Backend structure
    FastAPI -->|Routes| AuthRouter
    FastAPI -->|Routes| UsersRouter
    FastAPI -->|Routes| PlatformRouter
    FastAPI -->|Routes| AnalyticsRouter
    FastAPI -->|Routes| ActivityRouter
    FastAPI -->|Routes| ServiceRouter
    
    AuthRouter -->|Security| Security
    UsersRouter -->|Database Access| SQLAlchemy
    PlatformRouter -->|Database Access| SQLAlchemy
    AnalyticsRouter -->|Database Access| SQLAlchemy
    ActivityRouter -->|Database Access| SQLAlchemy
    ServiceRouter -->|Database Access| SQLAlchemy
    
    %% Data models
    SQLAlchemy -->|Maps to| Users
    SQLAlchemy -->|Maps to| PlatformUsers
    SQLAlchemy -->|Maps to| Campaigns
    SQLAlchemy -->|Maps to| Events
    SQLAlchemy -->|Maps to| Subscriptions
    SQLAlchemy -->|Maps to| Activities
    SQLAlchemy -->|Maps to| Services
    
    %% Database
    Users -->|SQL| PostgreSQL
    PlatformUsers -->|SQL| PostgreSQL
    Campaigns -->|SQL| PostgreSQL
    Events -->|SQL| PostgreSQL
    Subscriptions -->|SQL| PostgreSQL
    Activities -->|SQL| PostgreSQL
    Services -->|SQL| PostgreSQL
    
    PostgreSQL -->|Persists| Storage
    Alembic -->|Manages| PostgreSQL
    
    %% Docker infrastructure
    Vite -.->|Containerized| FrontendContainer
    FastAPI -.->|Containerized| BackendContainer
    PostgreSQL -.->|Containerized| DBContainer
    
    FrontendContainer -->|Orchestrated| Docker
    BackendContainer -->|Orchestrated| Docker
    DBContainer -->|Orchestrated| Docker
    
    %% Styling
    classDef client fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef frontend fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef backend fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef data fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef database fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef infra fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    
    class User,Browser client
    class React,Vite,Router,AxiosClient frontend
    class FastAPI,AuthRouter,UsersRouter,PlatformRouter,AnalyticsRouter,ActivityRouter,ServiceRouter,Security,SQLAlchemy backend
    class Users,PlatformUsers,Campaigns,Events,Subscriptions,Activities,Services data
    class PostgreSQL,Alembic,Storage database
    class Docker,FrontendContainer,BackendContainer,DBContainer infra
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant Frontend as 🌐 Frontend<br/>React
    participant Backend as 🔧 Backend<br/>FastAPI
    participant DB as 💾 Database<br/>PostgreSQL
    
    User->>Frontend: Enter credentials
    Frontend->>Backend: POST /auth/login<br/>(credentials)
    Backend->>DB: Query user by email
    DB-->>Backend: User record
    Backend->>Backend: Hash password +<br/>Verify (bcrypt)
    Backend->>Backend: Generate JWT token
    Backend-->>Frontend: JWT token + User data
    Frontend->>Frontend: Store JWT in<br/>localStorage
    Frontend->>Frontend: Set Authorization<br/>header (Axios interceptor)
    User->>Frontend: Access protected page
    Frontend->>Backend: GET /users/profile<br/>Authorization: Bearer {token}
    Backend->>Backend: Verify JWT token
    Backend->>DB: Query protected data
    DB-->>Backend: Data
    Backend-->>Frontend: Protected data
    Frontend->>User: Display data
```

## Docker Compose Services

```mermaid
graph LR
    subgraph compose["🐳 Docker Compose"]
        frontend["Frontend Container<br/>Port: 5173<br/>Node.js 20-Alpine"]
        backend["Backend Container<br/>Port: 8000<br/>Python 3.11-slim"]
        database["Database Container<br/>Port: 5432<br/>PostgreSQL 15"]
    end
    
    frontend -->|HTTP/REST| backend
    backend -->|SQL| database
    frontend -.->|depends_on| backend
    backend -.->|depends_on| database
    
    classDef service fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    classDef connection fill:#fff9c4,stroke:#f57f17,stroke-width:1px
    class frontend,backend,database service
```

## Technology Stack

```mermaid
graph TB
    subgraph frontend["Frontend Stack"]
        React["⚛️ React 19.2.0"]
        Vite["⚡ Vite 7.3.1"]
        Tailwind["🎨 Tailwind CSS 3.4.19"]
        MUI["💼 Material-UI 7.3.9"]
        Axios["📡 Axios 1.13.6"]
        Recharts["📊 Recharts 3.8.0"]
    end
    
    subgraph backend["Backend Stack"]
        FastAPI["🚀 FastAPI"]
        SQLAlchemy["🗄️ SQLAlchemy 2.0.46"]
        Pydantic["✅ Pydantic"]
        JOSE["🔐 python-jose"]
        Alembic["📝 Alembic 1.18.4"]
    end
    
    subgraph database["Database Stack"]
        PostgreSQL["🐘 PostgreSQL 15"]
        psycopg2["🔗 psycopg2-binary"]
    end
    
    subgraph infra["Infrastructure"]
        Docker["🐳 Docker"]
        Compose["🎭 Docker Compose"]
    end
    
    React --> Vite
    Axios --> React
    Tailwind --> React
    MUI --> React
    Recharts --> React
    
    FastAPI --> SQLAlchemy
    FastAPI --> Pydantic
    FastAPI --> JOSE
    Alembic --> SQLAlchemy
    
    SQLAlchemy --> psycopg2
    psycopg2 --> PostgreSQL
    
    Vite -.->|Containerized| Docker
    FastAPI -.->|Containerized| Docker
    PostgreSQL -.->|Containerized| Docker
    Docker --> Compose
    
    classDef frontend fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef backend fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    classDef database fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef infra fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    
    class React,Vite,Tailwind,MUI,Axios,Recharts frontend
    class FastAPI,SQLAlchemy,Pydantic,JOSE,Alembic backend
    class PostgreSQL,psycopg2 database
    class Docker,Compose infra
```

## Key Endpoints

```mermaid
graph TB
    API["🔧 FastAPI<br/>Base: http://localhost:8000"]
    
    API -->|Authentication| AUTH["/auth<br/>- POST /register<br/>- POST /login<br/>- JWT token mgmt"]
    
    API -->|Users| USERS["/users<br/>- GET /profile<br/>- GET /{id}<br/>- PATCH /update<br/>- DELETE /{id}"]
    
    API -->|Admin| PLATFORM["/platform-users<br/>- GET /<br/>- POST /create<br/>- PUT /update<br/>- DELETE /{id}"]
    
    API -->|Analytics| ANALYTICS["/analytics<br/>- GET /overview<br/>- GET /trends<br/>- GET /metrics"]
    
    API -->|Activity| ACTIVITY["/user-activity<br/>- GET /<br/>- POST /track<br/>- GET /{userId}"]
    
    API -->|Services| SERVICES["/service<br/>- GET /<br/>- POST /create<br/>- PUT /update"]
    
    classDef endpoint fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    classDef router fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    class API endpoint
    class AUTH,USERS,PLATFORM,ANALYTICS,ACTIVITY,SERVICES router
```

## Project Statistics

| Component | Details |
|-----------|---------|
| **Frontend** | React + Vite, Tailwind CSS, Material-UI |
| **Backend** | FastAPI (Python), SQLAlchemy ORM |
| **Database** | PostgreSQL 15 |
| **Frontend Port** | 5173 (Vite dev server) |
| **Backend Port** | 8000 (Uvicorn) |
| **Database Port** | 5432 (PostgreSQL) |
| **Authentication** | JWT + Bcrypt |
| **Infrastructure** | Docker + Docker Compose |
| **Persistence** | `postgres_data` volume |
| **Key Features** | Analytics Dashboard, User Management, Activity Tracking, Role-based Access |

