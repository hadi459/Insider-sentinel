"""
Generate a comprehensive PDF documentation of OOP concepts in backend/models.py
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.platypus import KeepTogether
from datetime import datetime

# Define colors
COLOR_PRIMARY = HexColor("#2E86AB")      # Blue
COLOR_SECONDARY = HexColor("#A23B72")   # Purple
COLOR_ACCENT = HexColor("#F18F01")      # Orange
COLOR_LIGHT_BG = HexColor("#F0F0F0")    # Light gray
COLOR_CODE_BG = HexColor("#1E1E1E")     # Dark gray
COLOR_CODE_TEXT = HexColor("#D4AF37")   # Gold

def create_oop_pdf(filename="OOP_Insider_Sentinel_Documentation.pdf"):
    """Generate comprehensive OOP documentation PDF"""
    
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=COLOR_PRIMARY,
        spaceAfter=12,
        alignment=1  # Center
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=COLOR_SECONDARY,
        spaceAfter=12,
        spaceBefore=12,
        borderColor=COLOR_PRIMARY,
        borderWidth=2,
        borderPadding=10,
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=COLOR_ACCENT,
        spaceAfter=8,
        spaceBefore=8,
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        alignment=4  # Justify
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Courier',
        textColor=COLOR_CODE_TEXT,
        backColor=COLOR_CODE_BG,
        leading=10,
        leftIndent=20,
        rightIndent=10,
    )
    
    # ========== COVER PAGE ==========
    story.append(Spacer(1, 1.5*inch))
    
    title = Paragraph("Object-Oriented Programming (OOP)", title_style)
    story.append(title)
    
    story.append(Spacer(1, 0.3*inch))
    
    subtitle = Paragraph(
        "Insider Sentinel - Complete Analysis & Documentation",
        ParagraphStyle('subtitle', parent=styles['Normal'], fontSize=16, alignment=1, textColor=COLOR_SECONDARY)
    )
    story.append(subtitle)
    
    story.append(Spacer(1, 0.5*inch))
    
    info_data = [
        ["Repository", "hadi459/Insider-sentinel"],
        ["File", "backend/models.py"],
        ["Date Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Focus", "Python OOP Implementation & Best Practices"],
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), COLOR_PRIMARY),
        ('TEXTCOLOR', (0, 0), (0, -1), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, COLOR_LIGHT_BG),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, COLOR_LIGHT_BG]),
    ]))
    story.append(info_table)
    
    story.append(PageBreak())
    
    # ========== TABLE OF CONTENTS ==========
    story.append(Paragraph("Table of Contents", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    toc_items = [
        "1. Overview of OOP Concepts",
        "2. Abstract Base Classes (ABC) - User Class",
        "3. Inheritance - Admin & Employee Classes",
        "4. Enumerations - UserRole, ActivityType, RiskLevel",
        "5. Properties & Encapsulation",
        "6. Dataclasses - ActivityLog & RiskProfile",
        "7. Composition - Dashboard & ReportGenerator",
        "8. Static Methods & Type Hints",
        "9. Complete Class Hierarchy Diagram",
        "10. Best Practices Summary",
    ]
    
    for item in toc_items:
        story.append(Paragraph(item, normal_style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # ========== 1. OOP OVERVIEW ==========
    story.append(Paragraph("1. Overview of OOP Concepts", heading1_style))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("What is Object-Oriented Programming?", heading2_style))
    story.append(Paragraph(
        "Object-Oriented Programming (OOP) is a programming paradigm based on organizing software design "
        "around objects and data, rather than functions and logic. Objects are instances of classes that bundle "
        "related data (attributes) and behavior (methods) together.",
        normal_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("Four Pillars of OOP:", heading2_style))
    
    pillars_data = [
        ["Pillar", "Description", "Example in Code"],
        ["Encapsulation", "Bundling data & methods; hiding internal details", "Private attributes: _user_id, _name"],
        ["Inheritance", "Deriving classes from parent class", "Admin & Employee inherit from User"],
        ["Polymorphism", "Same method name, different implementations", "get_dashboard_data() in Admin vs Employee"],
        ["Abstraction", "Defining interfaces via abstract classes", "@abstractmethod in User class"],
    ]
    
    pillars_table = Table(pillars_data, colWidths=[1.2*inch, 2*inch, 2.3*inch])
    pillars_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, COLOR_LIGHT_BG]),
    ]))
    story.append(pillars_table)
    story.append(PageBreak())
    
    # ========== 2. ABSTRACT BASE CLASSES ==========
    story.append(Paragraph("2. Abstract Base Classes (ABC) - User Class", heading1_style))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("What is an Abstract Class?", heading2_style))
    story.append(Paragraph(
        "An abstract class cannot be instantiated directly. It serves as a blueprint for subclasses and defines "
        "methods that must be implemented by child classes. This enforces a contract that all derived classes must follow.",
        normal_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("The User Class - ABC Example:", heading2_style))
    
    code_snippet1 = """from abc import ABC, abstractmethod

class User(ABC):
    \"\"\"Abstract base class for all system users.\"\"\"
    
    def __init__(self, user_id: int, name: str, email: str, 
                 role: UserRole, ...):
        self._user_id = user_id      # Private attribute (encapsulation)
        self._name = name
        self._email = email
        self._role = role
    
    @abstractmethod
    def get_dashboard_data(self) -> Dict:
        \"\"\"Return role-specific dashboard data.\"\"\"
        pass  # Child classes MUST implement this"""
    
    story.append(Paragraph(code_snippet1, code_style))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("Key Features:", heading2_style))
    features_abc = [
        "✓ <b>ABC inheritance:</b> Makes User an abstract class",
        "✓ <b>@abstractmethod:</b> Forces all subclasses to implement get_dashboard_data()",
        "✓ <b>Cannot instantiate:</b> user = User(...) would raise TypeError",
        "✓ <b>Template method:</b> Defines common interface for Admin and Employee classes",
    ]
    for feature in features_abc:
        story.append(Paragraph(feature, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    story.append(PageBreak())
    
    # ========== 3. INHERITANCE ==========
    story.append(Paragraph("3. Inheritance - Admin & Employee Classes", heading1_style))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("What is Inheritance?", heading2_style))
    story.append(Paragraph(
        "Inheritance allows a child class to inherit properties and methods from a parent class. "
        "It promotes code reuse and establishes an 'IS-A' relationship between classes.",
        normal_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("Admin Class - Example 1:", heading2_style))
    
    code_admin = """class Admin(User):
    \"\"\"Administrator with elevated privileges.\"\"\"
    
    DEFAULT_PERMISSIONS = frozenset([
        "view_all_employees",
        "block_employee",
        "force_logout",
        "generate_reports",
    ])
    
    def __init__(self, *args, permissions=None, **kwargs):
        kwargs.setdefault("role", UserRole.ADMIN)
        super().__init__(*args, **kwargs)  # Call parent __init__
        self._permissions = permissions or self.DEFAULT_PERMISSIONS
    
    def has_permission(self, perm: str) -> bool:
        return perm in self._permissions
    
    def get_dashboard_data(self) -> Dict:
        \"\"\"Implements abstract method from User\"\"\"
        return {
            "role": UserRole.ADMIN.value,
            "permissions": list(self._permissions),
        }"""
    
    story.append(Paragraph(code_admin, code_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("Employee Class - Example 2:", heading2_style))
    
    code_employee = """class Employee(User):
    \"\"\"Regular employee subject to monitoring.\"\"\"
    
    def __init__(self, *args, job_title: str = "", 
                 risk_score: float = 0.0, **kwargs):
        kwargs.setdefault("role", UserRole.EMPLOYEE)
        super().__init__(*args, **kwargs)
        self._job_title = job_title
        self._risk_score = max(0.0, min(1.0, risk_score))
        self._risk_level = RiskLevel.from_score(self._risk_score)
    
    def get_dashboard_data(self) -> Dict:
        \"\"\"Different implementation than Admin\"\"\"
        return {
            "role": UserRole.EMPLOYEE.value,
            "job_title": self._job_title,
            "risk_score": self._risk_score,
            "risk_level": self._risk_level.value,
        }"""
    
    story.append(Paragraph(code_employee, code_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("Key Inheritance Concepts:", heading2_style))
    inheritance_features = [
        "✓ <b>Extends User:</b> Both classes inherit user_id, name, email, is_blocked, etc.",
        "✓ <b>super().__init__():</b> Calls parent class constructor to initialize inherited attributes",
        "✓ <b>Polymorphism:</b> get_dashboard_data() has different logic in each class",
        "✓ <b>Method Overriding:</b> Child classes override abstract method with specific implementation",
        "✓ <b>Code Reuse:</b> Don't repeat password hashing, to_dict(), __repr__() methods",
    ]
    for feature in inheritance_features:
        story.append(Paragraph(feature, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    story.append(PageBreak())
    
    # ========== 4. ENUMERATIONS ==========
    story.append(Paragraph("4. Enumerations - UserRole, ActivityType, RiskLevel", heading1_style))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("What are Enums?", heading2_style))
    story.append(Paragraph(
        "Enums are special classes that contain a set of symbolic names (members) bound to unique, constant values. "
        "They provide type safety and prevent invalid values from being used.",
        normal_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("Example: UserRole Enum", heading2_style))
    
    code_enum = """from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"

# Usage:
user_role = UserRole.ADMIN
print(user_role.value)  # Output: "admin"
print(user_role == UserRole.ADMIN)  # Output: True"""
    
    story.append(Paragraph(code_enum, code_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("RiskLevel Enum with Class Method:", heading2_style))
    
    code_risklevel = """class RiskLevel(str, Enum):
    LOW = "low"              # 0.0 – 0.25
    MEDIUM = "medium"        # 0.25 – 0.50
    HIGH = "high"            # 0.50 – 0.75
    CRITICAL = "critical"    # 0.75 – 1.00
    
    @classmethod
    def from_score(cls, score: float) -> "RiskLevel":
        if score < 0.25:
            return cls.LOW
        elif score < 0.50:
            return cls.MEDIUM
        elif score < 0.75:
            return cls.HIGH
        return cls.CRITICAL

# Usage:
risk = RiskLevel.from_score(0.85)  # Returns RiskLevel.CRITICAL"""
    
    story.append(Paragraph(code_risklevel, code_style))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("Enums in Code:", heading2_style))
    enum_benefits = [
        "✓ <b>Type Safety:</b> Only valid values allowed (ADMIN or EMPLOYEE, not 'usr')",
        "✓ <b>Readability:</b> UserRole.ADMIN is clearer than just 'admin' string",
        "✓ <b>IDE Support:</b> Auto-completion for enum members",
        "✓ <b>ActivityType:</b> 13 defined types: LOGIN, LOGOUT, LINK_CLICKED, etc.",
        "✓ <b>Comparison:</b> Can compare enum members with == operator",
    ]
    for benefit in enum_benefits:
        story.append(Paragraph(benefit, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    story.append(PageBreak())
    
    # ========== 5. PROPERTIES & ENCAPSULATION ==========
    story.append(Paragraph("5. Properties & Encapsulation", heading1_style))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("What is Encapsulation?", heading2_style))
    story.append(Paragraph(
        "Encapsulation hides internal implementation details and protects object state. It's achieved using "
        "private attributes (prefixed with _) and public properties (@property decorators) for controlled access.",
        normal_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("Property Example - risk_score:", heading2_style))
    
    code_property = """class Employee(User):
    def __init__(self, risk_score: float = 0.0, **kwargs):
        self._risk_score = max(0.0, min(1.0, risk_score))
    
    @property
    def risk_score(self) -> float:
        \"\"\"Getter - read-only access to private attribute\"\"\"
        return self._risk_score
    
    @risk_score.setter
    def risk_score(self, value: float) -> None:
        \"\"\"Setter - validates and constrains input\"\"\"
        self._risk_score = max(0.0, min(1.0, value))  # Clamp to [0, 1]
        self._risk_level = RiskLevel.from_score(self._risk_score)

# Usage:
emp = Employee(name="John", risk_score=0.85)
print(emp.risk_score)  # Output: 0.85 (uses getter)
emp.risk_score = 1.5   # Setter validates: clamped to 1.0
print(emp.risk_score)  # Output: 1.0"""
    
    story.append(Paragraph(code_property, code_style))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("Encapsulation Benefits:", heading2_style))
    encap_benefits = [
        "✓ <b>Data Validation:</b> Setter ensures risk_score is always between 0.0 and 1.0",
        "✓ <b>Consistency:</b> Changing risk_score automatically updates risk_level",
        "✓ <b>Control:</b> Read-only access via @property (no setter)",
        "✓ <b>Flexibility:</b> Can change internal implementation without breaking API",
        "✓ <b>Private Attributes:</b> _user_id, _name, _email prevent direct modification",
    ]
    for benefit in encap_benefits:
        story.append(Paragraph(benefit, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    story.append(PageBreak())
    
    # ========== 6. DATACLASSES ==========
    story.append(Paragraph("6. Dataclasses - ActivityLog & RiskProfile", heading1_style))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("What are Dataclasses?", heading2_style))
    story.append(Paragraph(
        "Dataclasses automatically generate special methods (__init__, __repr__, __eq__) from class attributes. "
        "They reduce boilerplate code while maintaining type safety.",
        normal_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("ActivityLog Dataclass Example:", heading2_style))
    
    code_dataclass = """from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ActivityLog:
    log_id: int
    user_id: int
    activity_type: ActivityType
    description: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_address: str = ""
    metadata: Dict = field(default_factory=dict)
    
    def is_suspicious(self) -> bool:
        suspicious_types = {
            ActivityType.LINK_CLICKED,
            ActivityType.PRIVILEGE_ESCALATION,
            ActivityType.FAILED_LOGIN,
            ActivityType.DATA_EXPORT,
        }
        return self.activity_type in suspicious_types
    
    def to_dict(self) -> Dict:
        return {
            "log_id": self.log_id,
            "activity_type": self.activity_type.value,
            "timestamp": self.timestamp.isoformat(),
            "is_suspicious": self.is_suspicious(),
        }"""
    
    story.append(Paragraph(code_dataclass, code_style))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("Dataclass Auto-Generated Methods:", heading2_style))
    
    auto_methods = [
        "✓ <b>__init__:</b> Automatically generated from field annotations",
        "✓ <b>__repr__:</b> Readable string representation for debugging",
        "✓ <b>__eq__:</b> Equality comparison between instances",
        "✓ <b>field():</b> Use for complex defaults like dict, list, datetime.utcnow",
        "✓ <b>Methods:</b> Can add custom methods like is_suspicious() and to_dict()",
    ]
    for method in auto_methods:
        story.append(Paragraph(method, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    story.append(PageBreak())
    
    # ========== 7. COMPOSITION ==========
    story.append(Paragraph("7. Composition - Dashboard & ReportGenerator", heading1_style))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("What is Composition?", heading2_style))
    story.append(Paragraph(
        "Composition is 'HAS-A' relationship where a class contains instances of other classes. "
        "It's an alternative to inheritance and provides better flexibility and modularity.",
        normal_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("Dashboard Class - Composition Example:", heading2_style))
    
    code_composition = """class Dashboard:
    \"\"\"Aggregates analytics data for the admin overview.\"\"\"
    
    def __init__(self, monitoring_system) -> None:
        self._system = monitoring_system  # HAS-A relationship
    
    def get_overview_stats(self) -> Dict:
        return self._system.get_overview_stats()
    
    def get_employee_list(self) -> List[Dict]:
        return self._system.get_all_employees_with_risk()
    
    def get_heatmap_data(self) -> List[Dict]:
        return self._system.get_heatmap_data()

# Usage:
monitoring = MonitoringSystem(db)
dashboard = Dashboard(monitoring)
stats = dashboard.get_overview_stats()"""
    
    story.append(Paragraph(code_composition, code_style))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("Composition vs Inheritance:", heading2_style))
    
    comparison_data = [
        ["Aspect", "Composition (HAS-A)", "Inheritance (IS-A)"],
        ["Relationship", "Dashboard HAS-A MonitoringSystem", "Employee IS-A User"],
        ["Flexibility", "Easy to swap implementations", "More rigid hierarchy"],
        ["Code Reuse", "Delegates to other objects", "Inherits all methods"],
        ["Coupling", "Loose - dependent on interface", "Tight - bound to parent"],
        ["Use Case", "Multiple dependencies", "Single classification"],
    ]
    
    comp_table = Table(comparison_data, colWidths=[1.3*inch, 1.8*inch, 1.9*inch])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, COLOR_LIGHT_BG]),
    ]))
    story.append(comp_table)
    
    story.append(PageBreak())
    
    # ========== 8. STATIC METHODS & TYPE HINTS ==========
    story.append(Paragraph("8. Static Methods & Type Hints", heading1_style))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("Static Methods - No Instance Required:", heading2_style))
    
    code_static = """class User:
    @staticmethod
    def hash_password(password: str) -> str:
        \"\"\"Return a PBKDF2-HMAC-SHA256 password hash.\"\"\"
        salt = secrets.token_bytes(16)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
        return f"{salt.hex()}:{dk.hex()}"
    
    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        \"\"\"Verify plaintext password against stored hash.\"\"\"
        try:
            salt_hex, dk_hex = stored_hash.split(":", 1)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(dk_hex)
            actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
            return secrets.compare_digest(actual, expected)
        except (ValueError, TypeError):
            return False

# Usage - no instance needed:
hashed = User.hash_password("Secure@123")
is_valid = User.verify_password("Secure@123", hashed)"""
    
    story.append(Paragraph(code_static, code_style))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("Type Hints - Code Documentation & IDE Support:", heading2_style))
    
    code_types = """def __init__(
    self,
    user_id: int,              # int type
    name: str,                 # str type
    email: str,
    role: UserRole,            # Enum type
    department: str = "",      # default value
    is_active: bool = True,    # bool type
    created_at: Optional[datetime] = None,  # Optional
) -> None:                     # return type
    \"\"\"Type hints help IDE provide better autocomplete & catch errors.\"\"\"
    self._user_id: int = user_id
    self._name: str = name

def get_dashboard_data(self) -> Dict:
    \"\"\"Returns Dict type\"\"\"
    return {...}

def get_employees(self) -> List[Employee]:
    \"\"\"Returns List of Employee objects\"\"\"
    return [...]"""
    
    story.append(Paragraph(code_types, code_style))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("Type Hints Benefits:", heading2_style))
    type_benefits = [
        "✓ <b>IDE Support:</b> Better autocomplete and error detection",
        "✓ <b>Documentation:</b> Clear what types are expected and returned",
        "✓ <b>Type Checking:</b> Tools like mypy can validate code statically",
        "✓ <b>Static Methods:</b> Don't need instance, called on class directly",
        "✓ <b>Optional:</b> Allows None or specified type",
    ]
    for benefit in type_benefits:
        story.append(Paragraph(benefit, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    story.append(PageBreak())
    
    # ========== 9. CLASS HIERARCHY ==========
    story.append(Paragraph("9. Complete Class Hierarchy", heading1_style))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("Visual Class Hierarchy Diagram:", heading2_style))
    story.append(Spacer(1, 0.1*inch))
    
    hierarchy_text = """
    ┌─────────────────────────────────────────────────────────────────┐
    │                      BACKEND/MODELS.PY                          │
    │                    CLASS HIERARCHY STRUCTURE                     │
    └─────────────────────────────────────────────────────────────────┘
    
    ┌────────────────────────────────────────┐
    │            ENUMERATIONS                │
    ├────────────────────────────────────────┤
    │ • UserRole (ADMIN, EMPLOYEE)           │
    │ • ActivityType (13 types)              │
    │ • RiskLevel (LOW, MEDIUM, HIGH, etc.)  │
    └────────────────────────────────────────┘
                          │
    ┌─────────────────────┴──────────────────────┐
    │                                            │
    │      ┌────────────────────────────┐        │
    │      │   ABC: User (Abstract)     │        │
    │      ├────────────────────────────┤        │
    │      │ Attributes:                │        │
    │      │  - _user_id: int           │        │
    │      │  - _name: str              │        │
    │      │  - _email: str             │        │
    │      │  - _role: UserRole         │        │
    │      │  - _is_blocked: bool       │        │
    │      │  - _created_at: datetime   │        │
    │      │                            │        │
    │      │ Methods:                   │        │
    │      │  + @abstractmethod         │        │
    │      │    get_dashboard_data()    │        │
    │      │  + hash_password()         │        │
    │      │  + verify_password()       │        │
    │      │  + to_dict() -> Dict       │        │
    │      └────────────────────────────┘        │
    │               ▲          ▲                  │
    │      Inherited by   Inherited by            │
    │               │          │                  │
    │      ┌────────┘          └────────┐         │
    │      │                           │         │
    │      ▼                           ▼         │
    │  ┌──────────────┐        ┌──────────────┐  │
    │  │ Admin Class  │        │Employee Class│  │
    │  ├──────────────┤        ├──────────────┤  │
    │  │ + permissions│        │ + job_title  │  │
    │  │ + has_perm() │        │ + risk_score │  │
    │  │              │        │ + risk_level │  │
    │  │ Overrides:   │        │ + last_activ.│  │
    │  │ - get_dash..│        │              │  │
    │  │              │        │ Overrides:   │  │
    │  └──────────────┘        │ - get_dash..│  │
    │                          └──────────────┘  │
    │                                            │
    ├────────────────────────────────────────────┤
    │         DATACLASSES (no inheritance)       │
    │                                            │
    │    ┌─────────────────┐  ┌──────────────┐  │
    │    │  ActivityLog    │  │ RiskProfile  │  │
    │    ├─────────────────┤  ├──────────────┤  │
    │    │ + log_id: int   │  │ + employee.. │  │
    │    │ + user_id: int  │  │ + phishing.. │  │
    │    │ + activity_type │  │ + privilege..│  │
    │    │ + timestamp     │  │ + access_s..│  │
    │    │ + metadata      │  │ + frequency.│  │
    │    │                 │  │              │  │
    │    │ + is_suspicious │  │ + risk_level│  │
    │    │ + to_dict()     │  │ + to_dict() │  │
    │    └─────────────────┘  └──────────────┘  │
    │                                            │
    ├────────────────────────────────────────────┤
    │    COMPOSITION (HAS-A relationships)       │
    │                                            │
    │  ┌──────────────┐      ┌────────────────┐ │
    │  │  Dashboard   │      │ReportGenerator │ │
    │  ├──────────────┤      ├────────────────┤ │
    │  │ _system: MS  │      │ _system: MS    │ │
    │  │              │      │                │ │
    │  │ + get_stats()│      │ + generate()   │ │
    │  │ + get_emp..()│      │ + _report_*()  │ │
    │  │ + get_heat..│      │                │ │
    │  └──────────────┘      └────────────────┘ │
    │           ▲                    ▲           │
    │           └────────┬───────────┘           │
    │                    │                       │
    │       Both use MonitoringSystem             │
    │                                            │
    └────────────────────────────────────────────┘
    """
    
    story.append(Paragraph(hierarchy_text, ParagraphStyle(
        'Hierarchy',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7,
        leftIndent=10,
    )))
    
    story.append(PageBreak())
    
    # ========== 10. BEST PRACTICES ==========
    story.append(Paragraph("10. OOP Best Practices Summary", heading1_style))
    story.append(Spacer(1, 0.15*inch))
    
    practices_data = [
        ["Practice", "Description", "Insider Sentinel Example"],
        ["Single Responsibility", "Each class has one reason to change", "User only manages user data; Dashboard aggregates analytics"],
        ["DRY (Don't Repeat Yourself)", "Reuse code via inheritance/composition", "Admin & Employee inherit from User base class"],
        ["Encapsulation", "Hide internal details; expose interfaces", "Private _user_id, _name; public properties"],
        ["Type Hints", "Annotate parameter & return types", "def get_dashboard_data(self) -> Dict:"],
        ["Immutable Defaults", "Use frozenset for constants", "DEFAULT_PERMISSIONS = frozenset([...])"],
        ["Dataclasses", "Auto-generate boilerplate methods", "@dataclass for ActivityLog, RiskProfile"],
        ["Abstract Classes", "Define contracts for subclasses", "@abstractmethod get_dashboard_data()"],
        ["Composition > Inheritance", "Prefer composition for flexibility", "Dashboard has MonitoringSystem"],
        ["Magic Methods", "Implement __repr__, __eq__, etc.", "__repr__ for debugging, to_dict() for serialization"],
    ]
    
    practices_table = Table(practices_data, colWidths=[1.4*inch, 1.8*inch, 1.8*inch])
    practices_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, COLOR_LIGHT_BG]),
    ]))
    story.append(practices_table)
    
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("Key Takeaways:", heading2_style))
    takeaways = [
        "✓ <b>OOP in Insider Sentinel</b> demonstrates professional Python patterns",
        "✓ <b>Abstract User class</b> enforces contract for Admin and Employee",
        "✓ <b>Inheritance</b> eliminates code duplication and maintains consistency",
        "✓ <b>Enums</b> provide type safety and prevent invalid values",
        "✓ <b>Properties</b> enable data validation and controlled access",
        "✓ <b>Dataclasses</b> reduce boilerplate while maintaining clarity",
        "✓ <b>Composition</b> provides flexibility and separation of concerns",
        "✓ <b>Type hints</b> improve code quality and developer experience",
    ]
    for takeaway in takeaways:
        story.append(Paragraph(takeaway, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    story.append(Spacer(1, 0.4*inch))
    
    footer = Paragraph(
        f"<i>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        "Insider Sentinel - OOP Documentation | "
        "Repository: hadi459/Insider-sentinel | "
        "File: backend/models.py</i>",
        ParagraphStyle('footer', parent=styles['Normal'], fontSize=9, alignment=1, textColor=grey)
    )
    story.append(footer)
    
    # Build PDF
    doc.build(story)
    print(f"✅ PDF generated successfully: {filename}")

if __name__ == "__main__":
    create_oop_pdf()
