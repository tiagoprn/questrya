# ARCHITECTURE

## Summary

This application follows a **Layered Architecture** pattern that is tightly integrated with Flask and its ecosystem, particularly Flask-SQLAlchemy.

## Details

1. **Flask-Centric Layered Architecture**:
   - **API Layer**: Flask routes and blueprints in `pydo/api.py`
   - **Data Access Layer**: SQLAlchemy ORM models directly serving as both domain entities and data models
   - **Infrastructure Layer**: Extensions, configurations, and Celery integration

2. **Framework Coupling**:
   - Core entities (User, Task) directly inherit from `db.Model`, coupling domain logic to SQLAlchemy
   - Application factory pattern (`create_app()`) is Flask-specific
   - Authentication is implemented using Flask-JWT-Extended
   - Error handling is tied to Flask's error handling mechanisms

3. **Practical Separation of Concerns**:
   - Despite framework coupling, the code maintains good separation between different responsibilities
   - API endpoints, database models, background tasks, and configuration are logically separated
   - Testing is well-structured with appropriate fixtures and separation of test cases

## Classification

This is best described as a **Pragmatic Layered Architecture** that leverages Flask's ecosystem rather than a purist architectural approach. It prioritizes practical development patterns over strict architectural boundaries.

The application demonstrates a common real-world approach where:

- Framework features are embraced rather than abstracted away;

- ORM models serve dual purposes as both domain entities and data models;

- Business logic is on the models, following what's sometimes called the "Fat Models, Skinny Controllers" pattern.

### "Fat Models, Skinny Controllers" pattern:

Most of the business logic resides in the models rather than in the controllers (or in this case, API route handlers). The models are responsible not just for representing data structure but also for implementing business rules and operations. On the initial (and small) scope of this application this approach has advantages in keeping business logic centralized and reusable, but can potentially lead to large, complex model classes as the application grows.

The implementation can be described as:

1. The User model contains significant business logic:
   - Password hashing and verification (hash, check_password)
   - User registration and update operations (register, update)
   - Query methods for retrieving users (get_by)

2. In contrast, the API endpoints in pydo/api.py are relatively thin:
   - They seem to primarily handle HTTP requests/responses
   - Route parameters to the appropriate model methods
   - Handle authentication via JWT decorators

## Benefits of This Approach

1. **Development Efficiency**: Direct use of Flask and SQLAlchemy features accelerates development
2. **Framework Alignment**: Takes advantage of Flask's design patterns and conventions
3. **Reduced Boilerplate**: Avoids extra abstraction layers that would be needed in a strict Clean Architecture
4. **Practical Testability**: Still maintains good testability as evidenced by the comprehensive test suite

This architecture represents a practical balance between architectural purity and development pragmatism, which is common and often appropriate for applications with small scale and minimal complexity.

---

# ARCHITECTURE IMPROVEMENTS

Here are potential improvements to the current "Fat Models" architecture to address growing complexity with minimal overhead.

## Current Architecture Layout

This application currently follows a "Fat Models, Skinny Controllers" pattern where most business logic resides in the models. While this approach serves us well, it may lead to increasingly complex model classes as the application grows.

### Project Structure

``` bash

questrya/
├── __init__.py
├── api.py
├── commons.py
├── exceptions.py
├── extensions.py
├── factory.py
├── models.py
├── settings.py
├── tasks.py
└── tests
    ├── __init__.py
    ├── conftest.py
    ├── test_api.py
    ├── test_models.py
    └── utils.py

```

## New Architecture Layout

For this project, we will go with the "Vertical Slice Architecture".

That is an architectural pattern where an application is structured around feature-based slices rather than traditional horizontal layers (such as controllers, services, repositories, etc.).

Each "slice" represents a complete implementation of a feature, encapsulating all the necessary components like API, business logic, data access etc.

Being based in features (), it provides a pragmatic balance between proper software design and development simplicity.

By organizing code around features rather than technical layers and incorporating Celery for background processing, it improves cohesion while maintaining a clean separation of concerns.

The architecture is scalable, testable, and follows SOLID principles without introducing unnecessary complexity.

### Key Characteristics

- **Feature-Oriented**: Each slice represents an independent feature rather than a technical layer.
- **Encapsulation**: All necessary logic for a feature (business logic, orm, API, service, etc...) resides within its slice.
- **Independence**: Slices are designed to minimize dependencies between each other, promoting modularity.
- **Improves Maintainability**: Changes to a feature impact only its corresponding slice, reducing the risk of breaking unrelated functionality.
- **Scalability**: Easier to scale teams since developers can work on separate slices without conflicts.

### Project structure

``` bash
questrya/
├── __init__.py
├── common/                    # Shared utilities/code
│   ├── __init__.py
│   ├── exceptions.py
│   └── value_objects/
│       ├── __init__.py
│       ├── game_rating.py
│       └── email.py
├── games/                     # Game feature module
│   ├── __init__.py
│   ├── domain.py              # Game business logic
│   ├── repository.py          # Game data access
│   ├── service.py             # Game operations
│   ├── schemas.py             # Game serialization/validation
│   ├── routes.py              # Game API endpoints
├── users/                     # User feature module
│   ├── __init__.py
│   ├── domain.py
│   ├── repository.py
│   ├── service.py
│   ├── schemas.py
│   └── routes.py
├── workers/                   # Background processing
│   ├── __init__.py
│   ├── celery.py              # Celery configuration
│   ├── tasks/                 # Background tasks by domain
│   │   ├── __init__.py
│   │   ├── game_tasks.py      # Game-related background tasks
│   │   └── user_tasks.py      # User-related background tasks
│   └── schedules.py           # Scheduled tasks configuration
├── orm/               # Database configuration
│   ├── __init__.py
│   └── models.py              # ORM models (thin)
├── api/                       # API configuration
│   ├── __init__.py
│   └── api.py                 # Route registration
├── extensions.py              # Flask extensions
├── factory.py                 # App factory
└── settings.py                # Configuration
```

### Overview

| LAYER              | ROLE                                                                                 | CAN COMMUNICATE with     | MUST NOT COMMUNICATE with                             |
|--------------------|--------------------------------------------------------------------------------------|--------------------------|-------------------------------------------------------|
| Schemas            | request/response serialization/validation                                            | pydantic                 | ORM models, Repositories, Domain, Services, Routes    |
| Routes             | API endpoints                                                                        | Services, Schemas        | Repositories, Domain, ORM models                      |
| Services           | use cases (orchestrate domain & repositories)                                        | Repositories, Domain     | ORM models, Routes                                    |
| Domain (Core Logic)| pure python objects with business logic                                              | Nothing                  | ORM models, Repositories, Services, Routes            |
| Repositories       | persistence (translation between ORM & pure domain objects, ORM read/write queries)  | ORM models, Domain       | Services, Routes                                      |
| ORM models         | thin SQLAlchemy models                                                               | SQLAlchemy               | Domain, Repositories, Services, Routes                |

### Key Concepts Explained

#### Value Objects

Value objects are immutable objects defined entirely by their attributes, with no unique identity. They represent descriptive aspects of your domain that need validation or encapsulation of behavior.

**Example:** `GameRating` class as a value object.

```python
# common/value_objects/game_rating.py
class GameRating:
    def __init__(self, score):
        if not 1 <= score <= 10:
            raise ValueError(f"Rating must be between 1 and 10, got {score}")
        self._score = score

    @property
    def score(self):
        return self._score

    def is_recommended(self):
        return self._score >= 7
```

#### Domain

Domain objects encapsulate core business logic, rules, and behaviors central to your application. They represent the "what" of your system.

**Example:** `Game` domain object containing game state management and business rules.

```python
# games/domain.py
class Game:
    def __init__(self, id, title, platform, release_date, status, completion_date=None):
        self.id = id
        self.title = title
        self.platform = platform
        self.release_date = release_date
        self.status = status
        self.completion_date = completion_date

    def mark_completed(self, completion_date=None):
        if self.status == GameStatus.ABANDONED:
            raise InvalidGameStateError("Cannot complete an abandoned game")

        self.status = GameStatus.COMPLETED
        self.completion_date = completion_date or datetime.now()
```

#### Repository

Repositories abstract data access logic and provide methods to retrieve and persist domain objects. They act as collection-like interfaces for domain objects.

**Example:** `GameRepository` handling game orm and retrieval.

```python
# games/repository.py
class GameRepository:
    def get_by_id(self, game_id):
        game_model = GameModel.query.get(game_id)
        if not game_model:
            return None
        return self._to_domain(game_model)

    def get_backlog(self, user_id, status=None):
        query = GameModel.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status.value)
        return [self._to_domain(g) for g in query.all()]
```

#### Service

Services coordinate complex operations involving multiple domain objects or repositories. They implement application use cases and orchestrate business processes.

**Example:** `GameService` handling operations like game updates or status changes.

```python
# games/service.py
class GameService:
    def __init__(self, game_repository, user_repository):
        self.game_repository = game_repository
        self.user_repository = user_repository

    def add_to_backlog(self, title, platform, release_date, user_id):
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User not found")

        game = Game(
            id=None,
            title=title,
            platform=platform,
            release_date=release_date,
            status=GameStatus.NOT_STARTED,
            user_id=user_id
        )

        saved_game = self.game_repository.save(game)

        # Queue background task to fetch additional game info
        from workers.tasks.game_tasks import fetch_game_metadata
        fetch_game_metadata.delay(saved_game.id)

        return saved_game
```

#### Background Workers (Celery)

Background workers handle time-consuming or scheduled tasks that should run asynchronously outside the main request flow.

**Example:** Game metadata fetching task.

```python
# workers/tasks/game_tasks.py
from workers.celery import celery_app
from games.repository import GameRepository
from games.service import GameService

@celery_app.task
def fetch_game_metadata(game_id):
    """Fetch additional metadata for a game from external API"""
    repo = GameRepository()
    game = repo.get_by_id(game_id)

    if not game:
        return

    # Fetch metadata from external API
    # Update game with additional details
    # Save updated game
    repo.save(game)

@celery_app.task
def update_all_game_scores():
    """Update scores for all games from external rating services"""
    repo = GameRepository()
    games = repo.get_all()

    for game in games:
        # Update game scores
        # Save game
        repo.save(game)
```

**Celery Configuration:**

```python
# workers/celery.py
from celery import Celery
from questrya.settings import CELERY_BROKER_URL

celery_app = Celery('questrya', broker=CELERY_BROKER_URL)
celery_app.config_from_object('questrya.settings', namespace='CELERY')
celery_app.autodiscover_tasks(['questrya.workers.tasks'])
```

#### Schemas

Schemas handle data validation, serialization, and deserialization between API layer and domain objects. They define how data is presented externally.

**Example:** `GameSchema` for validating and formatting game data.

```python
# games/schemas.py
class GameSchema:
    def validate(self, data):
        errors = {}
        if not data.get('title'):
            errors['title'] = 'Title is required'
        if not data.get('platform'):
            errors['platform'] = 'Platform is required'
        if errors:
            raise ValidationError(errors)
        return data

    def to_dict(self, game):
        return {
            'id': game.id,
            'title': game.title,
            'platform': game.platform,
            'release_date': game.release_date.isoformat() if game.release_date else None,
            'status': game.status.value,
            'completion_date': game.completion_date.isoformat() if game.completion_date else None
        }
```

#### Routes

Routes define API endpoints and connect HTTP requests to appropriate service methods. They handle HTTP-specific concerns.

**Example:** Game API endpoints.

```python
# games/routes.py
@games_bp.route('/', methods=['POST'])
def add_game():
    data = request.get_json()
    game_schema = GameSchema()
    validated_data = game_schema.validate(data)

    game = game_service.add_to_backlog(
        title=validated_data['title'],
        platform=validated_data['platform'],
        release_date=validated_data.get('release_date'),
        user_id=g.current_user.id
    )

    return jsonify(game_schema.to_dict(game)), 201
```

#### Persistence

Persistence layer defines database models and handles database-specific configurations. In our architecture, these are kept thin and focused solely on data structure.

**Example:** Thin ORM models.

```python
# orm/models.py
class GameModel(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    release_date = db.Column(db.Date)
    status = db.Column(db.String(20), nullable=False)
    completion_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
```

#### API

API configuration handles application-wide API concerns like registering blueprints, middleware, and error handlers.

**Example:** API setup.

```python
# api/api.py
def register_blueprints(app):
    from games.routes import games_bp
    from users.routes import users_bp

    app.register_blueprint(games_bp, url_prefix='/api/games')
    app.register_blueprint(users_bp, url_prefix='/api/users')
```

### Celery Integration Details

#### Core Celery Setup

Celery is integrated as a separate module to handle all asynchronous processing needs:

1. **Configuration Separation**: Celery configuration lives in `workers/celery.py`
2. **Task Organization**: Tasks are grouped by domain in `workers/tasks/`
3. **Scheduled Tasks**: Defined in `workers/schedules.py`

#### Task Invocation Patterns

Tasks can be invoked from different places in the codebase:

1. **From Services**: When domain operations need background processing
   ```python
   # In a service method
   from workers.tasks.game_tasks import fetch_game_metadata
   fetch_game_metadata.delay(game_id)
   ```

2. **From Routes**: For direct API-triggered background tasks
   ```python
   # In a route handler
   from workers.tasks.game_tasks import sync_user_library

   @games_bp.route('/sync', methods=['POST'])
   def sync_games():
       task = sync_user_library.delay(g.current_user.id)
       return jsonify({'task_id': task.id}), 202
   ```

3. **As Scheduled Tasks**: For periodic operations
   ```python
   # In workers/schedules.py
   app.conf.beat_schedule = {
       'update-game-scores-daily': {
           'task': 'questrya.workers.tasks.game_tasks.update_all_game_scores',
           'schedule': crontab(hour=4, minute=0),  # Run at 4:00 AM
       },
   }
   ```

