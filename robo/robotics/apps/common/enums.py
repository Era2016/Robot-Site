from django_enumfield.enum import Enum


class NotificationVerb(object):
    APPLICATION_APPLIED = 'applied'
    APPLICATION_ACCEPTED = 'accepted'
    APPLICATION_REJECTED = 'rejected'

    APPLICATION_VERBS = [
        APPLICATION_APPLIED,
        APPLICATION_ACCEPTED,
        APPLICATION_REJECTED,
    ]

    TASK_COMPLETED = 'completed'
    TASK_RETURNED = 'returned'
    TASK_ASSIGNED = 'assigned'
    TASK_VERBS = [TASK_COMPLETED, TASK_RETURNED, TASK_ASSIGNED]

    JOB_POSTED = 'posted'
    RATING_LEFT = 'rated'
    COMMENT_POSTED = 'commented'


class UserRole(Enum):
    BUSINESS = 1
    WRITER = 2
    labels = {
        BUSINESS: 'Business',
        WRITER: 'Writer'
    }


class TaskType(Enum):
    WRITING = 1
    ACCEPT = 2
    EDITING = 3

    labels = {
        WRITING: 'Writing',
        ACCEPT: 'Accept',
        EDITING: 'Reviewing'
    }


class TaskStatus(Enum):
    INACTIVE = 1
    ACTIVE = 2
    FINISHED = 3

    labels = {
        INACTIVE: "Inactive",
        ACTIVE: "Active",
        FINISHED: "Finished",
    }


class WritingContentType(Enum):
    SHORT_BLOG_POST = 1
    LONG_BLOG_POST = 2
    WEBSITE_PAGE = 3
    ARTICLE = 4
    PRESS_RELEASE = 5

    labels = {
        SHORT_BLOG_POST: 'Short Blog Post',
        LONG_BLOG_POST: 'Long Blog Post',
        WEBSITE_PAGE: 'Website Page',
        ARTICLE: 'Article',
        PRESS_RELEASE: 'Press Release',
    }


class WritingGoal(Enum):
    GENERATE_CLICKS = 1
    PROVIDE_INFORMED_ANALYSIS = 2
    BUILD_THOUGHT_LEADERSHIP = 3
    REPURPOSE_EXISTING_WRITING = 4
    PROMOTE_TOPIC = 5
    EDUCATE_INSTRUCT = 6

    labels = {
        GENERATE_CLICKS: "Generate Clicks",
        PROVIDE_INFORMED_ANALYSIS: "Provide Informed Analysis",
        BUILD_THOUGHT_LEADERSHIP: "Build Thought Leadership",
        REPURPOSE_EXISTING_WRITING: "Repurpose Existing Writing",
        PROMOTE_TOPIC: "Promote Topic",
        EDUCATE_INSTRUCT: "Eduate Instruct",
    }


class WritingStyle(Enum):
    AUTHORATIATIVE = 1
    FORMAL = 2
    INSTRUCTIONAL = 3
    VIRAL = 4
    CASUAL = 5
    WITTY = 6

    labels = {
        AUTHORATIATIVE: "Authoratiative",
        FORMAL: "Formal",
        INSTRUCTIONAL: "Instructional",
        VIRAL: "Viral",
        CASUAL: "Casual",
        WITTY: "Witty",
    }


class WritingPointOfView(Enum):
    FIRST_PERSON = 1
    SECOND_PERSON = 2
    THIRD_PERSON = 3

    labels = {
        FIRST_PERSON: "1st Person",
        SECOND_PERSON: "2nd Person",
        THIRD_PERSON: "3rd Person",
    }


class ApplicationStatus(Enum):
    PENDING = 1
    REJECTED = 2
    ACCEPTED = 3

    labels = {
        PENDING: 'Pending',
        REJECTED: 'Rejected',
        ACCEPTED: 'Accepted',
    }


class JobCanView(Enum):
    INTERNAL = 1
    EXTERNAL = 2

    labels = {
        INTERNAL: 'Internal',
        EXTERNAL: 'External',
    }
