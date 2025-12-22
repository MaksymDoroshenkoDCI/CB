DOC_OUTLINE_PROMPT = """
You are an experienced systems analyst and technical documentation writer for IT systems.

Based on the IT system description below, create a detailed structure for technical documentation.

{project_context}

System description:
{user_input}

Create a documentation structure that includes:
1. Introduction and general system overview
2. System architecture (general, components, diagrams)
3. Tech stack (programming languages, frameworks, databases, tools)
4. Functionality (main modules, features, use cases)
5. API and integrations (endpoints, external services)
6. Database (schema, data models, migrations)
7. Security (authentication, authorization, data protection)
8. Deployment and infrastructure (deployment, CI/CD, servers)
9. Testing (strategy, test types, coverage)
10. Monitoring and logging
11. Developer documentation (getting started, contribution guide)

Return the answer as a detailed structured list with markers and subsections.
"""

DOC_DRAFT_PROMPT = """
You are a professional technical writer with experience creating documentation for IT projects.

Based on this documentation structure and system description, create a detailed draft of technical documentation.

{project_context}

DOCUMENTATION STRUCTURE:
{outline}

SYSTEM DESCRIPTION:
{user_input}

Documentation requirements:
- Write formally but clearly
- Use technical terms correctly
- Add code examples, diagrams (text descriptions), configurations where appropriate
- Include details about architecture, technologies, processes
- Describe not only "what", but also "how" and "why"
- Add practical usage examples
- Include information about dependencies and integrations
- Describe development and deployment processes

Create comprehensive technical documentation that can be used for onboarding new developers and maintaining the system.
"""

DOC_REFINEMENT_PROMPT = """
You are an experienced editor of technical documentation for IT projects.

Here is the document draft:
{draft}

Optimize and improve the text:
- make the style more uniform and professional
- remove repetitions and redundant information
- clarify technical formulations
- ensure the structure is logical and consistent
- add transitions between sections for better readability
- check that all technical terms are used correctly
- ensure formatting consistency (headings, lists, code)
- make sure the documentation is complete and useful for developers

Return only the edited, final text of the documentation without additional comments.
"""
