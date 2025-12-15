# Detailed Explanation: ResearchSession Model

## Table of Contents
1. [File Structure Overview](#file-structure-overview)
2. [Imports and Dependencies](#imports-and-dependencies)
3. [Class Definition and Inheritance](#class-definition-and-inheritance)
4. [Inner Class: Status Choices](#inner-class-status-choices)
5. [Field-by-Field Breakdown](#field-by-field-breakdown)
6. [Meta Class](#meta-class)
7. [String Representation](#string-representation)
8. [Django ORM Concepts](#django-orm-concepts)
9. [Python Concepts Used](#python-concepts-used)

---

## File Structure Overview

This file defines a Django **Model** - a Python class that represents a database table. Django uses an ORM (Object-Relational Mapping) that automatically converts Python classes into SQL tables and provides methods to interact with the database.

```
research_session.py
├── Module-level docstring (lines 1-5)
├── Imports (lines 8-10)
└── ResearchSession class
    ├── Inner Status class
    ├── Field definitions
    ├── Meta class
    └── __str__ method
```

---

## Imports and Dependencies

### `import uuid`
```python
import uuid
```
- **What it is**: Python's built-in UUID (Universally Unique Identifier) module
- **Why we need it**: Generates unique 128-bit identifiers (e.g., `550e8400-e29b-41d4-a716-446655440000`)
- **Python concept**: Standard library module - no installation needed
- **Use case**: Creating unique primary keys that are globally unique (not just unique in our database)

### `from django.db import models`
```python
from django.db import models
```
- **What it is**: Django's database models module
- **Why we need it**: Provides base classes and field types for defining database models
- **Django concept**: Core ORM functionality
- **Provides**: `Model` base class, field types (`CharField`, `TextField`, `ForeignKey`, etc.)

### `from django.utils import timezone`
```python
from django.utils import timezone
```
- **What it is**: Django's timezone utility
- **Why we need it**: Handles timezone-aware datetime objects
- **Django concept**: Timezone handling (Django stores datetimes in UTC)
- **Use case**: `timezone.now()` returns current time in UTC, respecting Django's timezone settings

---

## Class Definition and Inheritance

```python
class ResearchSession(models.Model):
```

### Python Concepts:

**1. Class Definition**
- `class` keyword creates a new class
- `ResearchSession` is the class name (PascalCase convention for classes)

**2. Inheritance**
- `(models.Model)` means ResearchSession **inherits** from Django's `Model` class
- **Inheritance**: Child class gets all methods and properties from parent class
- **Why inherit from Model?**
  - Gets database interaction methods (`save()`, `delete()`, `objects.all()`, etc.)
  - Django automatically creates database table from this class
  - Enables Django admin interface
  - Provides validation and serialization

**3. Docstring**
```python
"""
Model representing a research session in a deep research system.
Tracks the lifecycle of a research query from initiation to completion.
"""
```
- Triple-quoted string that documents the class
- Python convention for documentation
- Accessible via `ResearchSession.__doc__`

---

## Inner Class: Status Choices

```python
class Status(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    RUNNING = 'RUNNING', 'Running'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'
```

### Python Concepts:

**1. Inner/Nested Class**
- Class defined inside another class
- `Status` is a class inside `ResearchSession`
- Accessible as `ResearchSession.Status.PENDING`

**2. Django Concept: TextChoices**
- `models.TextChoices` is a Django enum-like class
- Provides both database value and human-readable label
- Format: `NAME = 'db_value', 'Human Label'`

**3. Tuple Assignment**
```python
PENDING = 'PENDING', 'Pending'
```
- Python creates a tuple: `('PENDING', 'Pending')`
- First value: stored in database
- Second value: displayed in admin/forms

**4. Why Use Choices?**
- **Data integrity**: Only valid values can be stored
- **Type safety**: Django validates on save
- **Admin interface**: Shows dropdown instead of text input
- **Code clarity**: `ResearchSession.Status.PENDING` is clearer than `'PENDING'`

**Usage Example:**
```python
session = ResearchSession()
session.status = ResearchSession.Status.PENDING  # ✅ Valid
session.status = 'INVALID'  # ❌ Raises validation error
```

---

## Field-by-Field Breakdown

### 1. Primary Key: UUID

```python
id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
```

**Django Field Type: `UUIDField`**
- Stores UUID (128-bit identifier)
- Database type: Usually `CHAR(36)` or `UUID` type

**Parameters:**
- `primary_key=True`: This field is the primary key (unique identifier for each row)
- `default=uuid.uuid4`: Python function called to generate default value
  - `uuid.uuid4()` generates random UUID each time
  - Called when object is created (not when class is defined)
- `editable=False`: Field won't appear in Django admin forms (auto-generated)

**Why UUID instead of auto-incrementing integer?**
- **Security**: Can't guess other IDs (prevents enumeration attacks)
- **Distributed systems**: Multiple servers can generate unique IDs without coordination
- **Privacy**: Doesn't reveal how many records exist

**Python Concept: Function as Default**
- `uuid.uuid4` is a function reference (not a function call)
- Django calls it when creating new objects
- If we wrote `default=uuid.uuid4()`, it would generate one UUID at import time (wrong!)

---

### 2. User ID

```python
user_id = models.IntegerField()
```

**Django Field Type: `IntegerField`**
- Stores integer values
- Database type: `INTEGER`

**Why IntegerField?**
- Simple, fast lookups
- Can be migrated to ForeignKey later if needed
- No foreign key constraint yet (flexibility)

**Future Migration Path:**
```python
# Later, can become:
user_id = models.ForeignKey(User, on_delete=models.CASCADE)
```

---

### 3. Original Query

```python
original_query = models.TextField()
```

**Django Field Type: `TextField`**
- Stores unlimited-length text
- Database type: `TEXT` (vs `VARCHAR` for CharField)

**TextField vs CharField:**
- `CharField`: Has `max_length` parameter, stored as `VARCHAR`
- `TextField`: No length limit, stored as `TEXT`
- Use TextField for user-generated content of unknown length

**Why not nullable?**
- Every research session must have a query
- `blank=False` (default) means required in forms
- `null=False` (default) means required in database

---

### 4. Status Field

```python
status = models.CharField(
    max_length=20,
    choices=Status.choices,
    default=Status.PENDING
)
```

**Django Field Type: `CharField`**
- Stores fixed-length strings
- `max_length=20`: Maximum characters (required for CharField)
- Database type: `VARCHAR(20)`

**Parameters:**
- `choices=Status.choices`: Restricts values to Status enum
  - `Status.choices` returns list of tuples: `[('PENDING', 'Pending'), ...]`
- `default=Status.PENDING`: New sessions start as PENDING
  - Uses the database value (`'PENDING'`), not the tuple

**Why Status is Critical for Async Jobs:**

In synchronous code:
```python
result = do_research()  # Waits until done
return result
```

In asynchronous code (like this system):
```python
session = ResearchSession.objects.create(query="...")
start_research_task(session.id)  # Returns immediately
# Client polls: session.status == 'RUNNING'?
# Later: session.status == 'COMPLETED'
```

**Status Flow:**
1. `PENDING`: Created but not started
2. `RUNNING`: Research task is executing
3. `COMPLETED`: Research finished successfully
4. `FAILED`: Research encountered an error

**Client Polling Example:**
```python
# Client code
session = ResearchSession.objects.get(id=session_id)
while session.status == 'RUNNING':
    time.sleep(5)  # Wait 5 seconds
    session.refresh_from_db()  # Get latest status
if session.status == 'COMPLETED':
    return session.final_report
```

---

### 5. Final Report

```python
final_report = models.TextField(blank=True, null=True)
```

**Parameters:**
- `blank=True`: Field can be empty in Django forms
- `null=True`: Field can be `NULL` in database

**Why Both?**
- `blank=True`: Form validation (user can submit empty)
- `null=True`: Database constraint (column allows NULL)
- For TextField, usually use both together

**Why Nullable?**
- Report only exists when research completes
- PENDING/RUNNING sessions don't have reports yet
- FAILED sessions might not have reports

---

### 6. Self-Referencing Foreign Key

```python
parent_research = models.ForeignKey(
    'self',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='child_researches'
)
```

**Django Field Type: `ForeignKey`**
- Creates relationship between two records
- Database: Creates foreign key column + index

**Parameters Explained:**

**1. `'self'` (String Reference)**
- References the same model (self-referencing)
- String `'self'` used because class isn't fully defined yet
- Could also use `ResearchSession` after class is defined

**2. `on_delete=models.SET_NULL`**
- What happens when parent is deleted?
- `SET_NULL`: Set this field to `NULL` (keeps child record)
- Other options:
  - `CASCADE`: Delete child when parent deleted
  - `PROTECT`: Prevent parent deletion if children exist
  - `DO_NOTHING`: Database handles it

**3. `null=True, blank=True`**
- `null=True`: Database allows NULL
- `blank=True`: Forms allow empty
- Not all sessions have parents (top-level sessions)

**4. `related_name='child_researches'`**
- Creates reverse relationship
- Access children: `parent.child_researches.all()`
- Without this: Django auto-creates `researchsession_set` (ugly)

**Real-World Example:**
```python
# Initial research
session1 = ResearchSession.objects.create(
    original_query="What is AI?",
    user_id=1
)

# Follow-up research
session2 = ResearchSession.objects.create(
    original_query="Tell me more about neural networks",
    user_id=1,
    parent_research=session1  # Builds on session1
)

# Access relationships
session1.child_researches.all()  # Returns [session2]
session2.parent_research  # Returns session1
```

**Tree Structure:**
```
Session1 (What is AI?)
  └── Session2 (Tell me about neural networks)
       └── Session3 (Explain backpropagation)
```

---

### 7. Trace ID

```python
trace_id = models.CharField(max_length=255, blank=True, null=True)
```

**Why Store Trace ID?**

In AI systems using LangSmith/LangChain:
- Every LLM call gets a trace ID
- Traces show: which models called, tokens used, latency, costs
- Storing trace_id links database record to observability platform

**Example Workflow:**
```python
# Research starts
with langsmith.trace() as trace:
    result = llm.call("Research: " + query)
    session.trace_id = trace.id
    session.save()

# Later, view trace in LangSmith UI
# Search by trace_id to see all LLM calls for this session
```

---

### 8. Timestamps

```python
created_at = models.DateTimeField(default=timezone.now)
updated_at = models.DateTimeField(auto_now=True)
```

**Django Field Type: `DateTimeField`**
- Stores date and time
- Database type: `DATETIME` or `TIMESTAMP`

**Two Different Patterns:**

**1. `created_at` with `default=timezone.now`**
- `timezone.now` is function reference (like uuid.uuid4)
- Called once when object is created
- Value doesn't change after creation
- Can be manually set if needed

**2. `updated_at` with `auto_now=True`**
- Automatically set to current time on EVERY save
- Cannot be manually overridden
- Always reflects last modification time

**Why Both?**
- `created_at`: When was this record created? (immutable)
- `updated_at`: When was it last changed? (mutable)

**Usage:**
```python
session = ResearchSession.objects.create(...)
print(session.created_at)  # 2024-01-15 10:00:00
print(session.updated_at)  # 2024-01-15 10:00:00

session.status = 'RUNNING'
session.save()
print(session.created_at)  # 2024-01-15 10:00:00 (unchanged)
print(session.updated_at)  # 2024-01-15 10:05:00 (updated!)
```

---

## Meta Class

```python
class Meta:
    ordering = ['-created_at']
    verbose_name = 'Research Session'
    verbose_name_plural = 'Research Sessions'
```

**Python Concept: Inner Class**
- `Meta` is a special inner class
- Django reads it for model configuration
- Not a database table - just configuration

**Options Explained:**

**1. `ordering = ['-created_at']`**
- Default ordering for queries
- `-` prefix means descending (newest first)
- Without `-`: ascending (oldest first)
- Affects: `ResearchSession.objects.all()` returns newest first

**2. `verbose_name`**
- Human-readable singular name
- Used in Django admin: "Add Research Session"

**3. `verbose_name_plural`**
- Human-readable plural name
- Used in Django admin: "Research Sessions" (not "Research Sessionss")

**Other Common Meta Options:**
```python
class Meta:
    db_table = 'custom_table_name'  # Override table name
    indexes = [models.Index(fields=['user_id'])]  # Database indexes
    unique_together = [['user_id', 'query']]  # Unique constraints
```

---

## String Representation

```python
def __str__(self):
    return f"ResearchSession {self.id} - {self.status}"
```

**Python Concept: Magic Method**
- `__str__` is called when object is converted to string
- Used in: `print()`, Django admin, templates, error messages

**Python Concept: f-strings**
- `f"..."` is formatted string literal (Python 3.6+)
- `{self.id}` and `{self.status}` are expressions evaluated and inserted
- Equivalent to: `"ResearchSession " + str(self.id) + " - " + str(self.status)`

**Why Define __str__?**
- Without it: `<ResearchSession object (550e8400-...)>` (ugly)
- With it: `ResearchSession 550e8400-... - PENDING` (readable)
- Django admin shows this in list views

**Usage:**
```python
session = ResearchSession.objects.get(id=some_id)
print(session)  # Calls __str__()
# Output: "ResearchSession 550e8400-... - COMPLETED"
```

---

## Django ORM Concepts

### How This Model Becomes a Database Table

When you run `python manage.py makemigrations`:
1. Django reads this class
2. Generates migration file (SQL operations)
3. Migration creates table like:

```sql
CREATE TABLE research_researchsession (
    id UUID PRIMARY KEY,
    user_id INTEGER NOT NULL,
    original_query TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    final_report TEXT,
    parent_research_id UUID REFERENCES research_researchsession(id),
    trace_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

### Using the Model

**Create:**
```python
session = ResearchSession.objects.create(
    user_id=1,
    original_query="What is machine learning?",
    status=ResearchSession.Status.PENDING
)
```

**Read:**
```python
# Get all
sessions = ResearchSession.objects.all()

# Filter
pending = ResearchSession.objects.filter(status='PENDING')

# Get one
session = ResearchSession.objects.get(id=some_uuid)
```

**Update:**
```python
session.status = 'COMPLETED'
session.final_report = "Machine learning is..."
session.save()  # updated_at automatically updated
```

**Delete:**
```python
session.delete()
```

---

## Python Concepts Used

### 1. **Class Attributes vs Instance Attributes**
- Fields defined in class are **class attributes**
- When you create instance: `session = ResearchSession()`, Django creates **instance attributes**
- Each instance has its own values

### 2. **Type Hints (Not Used Here, But Could Be)**
```python
# Could add:
from typing import Optional
from uuid import UUID

id: UUID
user_id: int
status: str
parent_research: Optional['ResearchSession']
```

### 3. **Property Decorators (Not Used, But Available)**
```python
@property
def is_completed(self):
    return self.status == self.Status.COMPLETED
```

### 4. **Method Overriding**
- `__str__` overrides parent class method
- Django's Model has default `__str__`, we replace it

---

## Summary

This model file demonstrates:
- **Django ORM**: Converting Python class to database table
- **Python OOP**: Classes, inheritance, inner classes
- **Database Design**: Primary keys, foreign keys, constraints
- **Async Patterns**: Status tracking for background jobs
- **Best Practices**: UUIDs, timestamps, self-documenting code

The model serves as the foundation for a deep research system where:
1. Users submit queries
2. Research runs asynchronously
3. Status is tracked through lifecycle
4. Results are stored when complete
5. Research can build on previous research
6. Everything is traceable and auditable

