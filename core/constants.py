class WorkflowState:
    DRAFT = 'DRAFT'
    CONCEPT_SUBMITTED = 'CONCEPT_SUBMITTED'
    DEPARTMENT_REVIEW = 'DEPARTMENT_REVIEW'
    DEPARTMENT_APPROVED = 'DEPARTMENT_APPROVED'
    SUPERVISOR_ASSIGNED = 'SUPERVISOR_ASSIGNED'
    UNDER_SUPERVISION = 'UNDER_SUPERVISION'
    PROPOSAL_SUBMITTED = 'PROPOSAL_SUBMITTED'
    SCHOOL_REVIEW = 'SCHOOL_REVIEW'
    SCHOOL_APPROVED = 'SCHOOL_APPROVED'
    ETHICS_REVIEW = 'ETHICS_REVIEW'
    ETHICS_APPROVED = 'ETHICS_APPROVED'
    RESEARCH_REGISTERED = 'RESEARCH_REGISTERED'
    EXTERNAL_REVIEW = 'EXTERNAL_REVIEW'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'

    CHOICES = [
        (DRAFT, 'Draft'),
        (CONCEPT_SUBMITTED, 'Concept Submitted'),
        (DEPARTMENT_REVIEW, 'Department Review'),
        (DEPARTMENT_APPROVED, 'Department Approved'),
        (SUPERVISOR_ASSIGNED, 'Supervisor Assigned'),
        (UNDER_SUPERVISION, 'Under Supervision'),
        (PROPOSAL_SUBMITTED, 'Proposal Submitted'),
        (SCHOOL_REVIEW, 'School Review'),
        (SCHOOL_APPROVED, 'School Approved'),
        (ETHICS_REVIEW, 'Ethics Review'),
        (ETHICS_APPROVED, 'Ethics Approved'),
        (RESEARCH_REGISTERED, 'Research Registered'),
        (EXTERNAL_REVIEW, 'External Review'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]


class Roles:
    STUDENT = 'STUDENT'
    SUPERVISOR = 'SUPERVISOR'
    HOD = 'HOD'
    DEPARTMENT_COMMITTEE = 'DEPARTMENT_COMMITTEE'
    SCHOOL_COMMITTEE = 'SCHOOL_COMMITTEE'
    ETHICS_COMMITTEE = 'ETHICS_COMMITTEE'
    RESEARCH_OFFICE_ADMIN = 'RESEARCH_OFFICE_ADMIN'
    EXTERNAL_EXAMINER = 'EXTERNAL_EXAMINER'

    CHOICES = [
        (STUDENT, 'Student'),
        (SUPERVISOR, 'Supervisor'),
        (HOD, 'Head of Department'),
        (DEPARTMENT_COMMITTEE, 'Department Committee'),
        (SCHOOL_COMMITTEE, 'School Committee'),
        (ETHICS_COMMITTEE, 'Ethics Committee'),
        (RESEARCH_OFFICE_ADMIN, 'Research Office Admin'),
        (EXTERNAL_EXAMINER, 'External Examiner'),
    ]
