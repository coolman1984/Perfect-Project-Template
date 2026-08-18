"""FACTORY — turns business knowledge into a technical project contract.

    THE USER PROVIDES BUSINESS KNOWLEDGE.
    THE TEMPLATE STEERS THE AI AGENT.
    THE AGENT IMPLEMENTS WITHIN CONTROLLED BOUNDARIES.
    MACHINE GATES VERIFY THE RESULT.
    THE USER APPROVES BUSINESS MEANING AND RESULTS.

The Factory runs at SETUP time, before and around the application. Like the tool
tier it is standard-library only (Constitution Part 37.2), so an employee or an
agent can run it in a bare workspace with nothing installed.

Boundaries this package must respect:
  * it never decides a Part 3.1 human-owned value — it collects and translates
  * it never records an approval on a human's behalf (Part 41.3)
  * it never imports the application runtime, and the application never imports it
"""

__all__ = ["approvals", "questionnaire", "generator", "build_brief", "health"]
