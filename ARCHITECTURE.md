# ARCHITECTURE

## Summary

This project implements Clean Architecture with a Feature-First approach, combining Domain-Driven Design principles with a practical organization strategy.

Instead of traditional horizontal layers (controllers, services, repositories) that span across the entire application, the codebase is organized around feature modules (users, auth, monitor) that then have the layers defined inside each one of them.

## Characteristics

• Feature-Oriented: Each module represents a complete, independent feature rather than a technical layer

• Encapsulation: All necessary components (domain logic, repositories, services, API endpoints) reside within their respective feature modules, keeping related code together for better understanding

• Modularity: Features are designed with minimal dependencies between each other, ensuring changes to one feature have minimal impact on others

• Contextual Clarity: Developers can understand and modify a complete feature in one location without navigating across disparate technical layers

• Scalability: Easier to scale teams since developers can work on separate features without conflicts

• Balanced Design: The structure maintains clean architecture principles while prioritizing practical maintainability

This approach creates a codebase that is both well-structured and pragmatic, balancing architectural purity with development efficiency.

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

