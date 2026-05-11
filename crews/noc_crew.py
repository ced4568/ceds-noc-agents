from crewai import Agent, Task, Crew, LLM

llm = LLM(
    model="ollama/mistral:7b",
    base_url="http://10.10.30.135:11434"
)

infra_analyst = Agent(
    role="Infrastructure Analyst",
    goal="Analyze infrastructure metrics and identify anomalies",
    backstory="You are a senior infrastructure analyst at Ced's Home Lab NOC. You monitor Proxmox clusters, K3s nodes, and network health. You are direct, technical, and concise.",
    llm=llm,
    verbose=True
)

rca_analyst = Agent(
    role="Root Cause Analyst",
    goal="Determine the root cause of infrastructure issues",
    backstory="You are a root cause analysis expert. You take infrastructure findings and determine the most likely cause and impact. You think systematically and document findings clearly.",
    llm=llm,
    verbose=True
)

doc_writer = Agent(
    role="NOC Documentation Writer",
    goal="Write clear incident reports from technical findings",
    backstory="You write structured incident reports for Ced's Home Lab. Your reports are concise, actionable, and follow NOC standards.",
    llm=llm,
    verbose=True
)

analyze_task = Task(
    description="Analyze this alert: K3s-Node-4 unreachable for 5 minutes. CPU on remaining nodes spiked to 85 percent. Prometheus scrape target down. Pod rescheduling on K3s-Node-5 and K3s-Node-6. Identify key symptoms and affected systems.",
    agent=infra_analyst,
    expected_output="A bullet point list of symptoms and affected systems"
)

rca_task = Task(
    description="Based on analyst findings determine: 1. Most likely root cause 2. Impact on cluster 3. Immediate recommended actions",
    agent=rca_analyst,
    expected_output="Root cause, impact assessment, and 3 recommended actions"
)

doc_task = Task(
    description="Write a structured NOC incident report with: Incident Summary, Affected Systems, Root Cause, Impact, Recommended Actions, Priority Level",
    agent=doc_writer,
    expected_output="A complete formatted NOC incident report"
)

noc_crew = Crew(
    agents=[infra_analyst, rca_analyst, doc_writer],
    tasks=[analyze_task, rca_task, doc_task],
    verbose=True
)

print("\n Starting Ced's NOC Analyst Crew...\n")
result = noc_crew.kickoff()
print("\n FINAL INCIDENT REPORT:")
print(result)