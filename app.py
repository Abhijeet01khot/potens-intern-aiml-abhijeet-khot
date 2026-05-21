import json
import streamlit as st

from agent import run_triage_agent, CATEGORIES, PRIORITIES


st.set_page_config(
    page_title="Smart Ticket Triage Agent",
    page_icon="🎫",
    layout="wide"
)


def show_reasoning_tree(reasoning_trace):
    """
    Displays the reasoning trace in a simple tree-like format.
    This satisfies the requirement that the reasoning trace should be visible.
    """
    for step in reasoning_trace:
        step_number = step.get("step", "")
        step_name = step.get("name", "step")
        details = step.get("details", {})

        with st.expander(f"Step {step_number}: {step_name}", expanded=False):
            st.json(details)


st.title("🎫 Smart Ticket Triage Agent")
st.caption(
    "AI/ML internship take-home project: free-text ticket triage with real callable tools."
)

st.divider()

with st.sidebar:
    st.header("Priority Scheme")

    for priority, description in PRIORITIES.items():
        st.markdown(f"**{priority}**")
        st.write(description)

    st.divider()

    st.header("Categories")
    for category in CATEGORIES:
        st.write(f"- {category.title()}")

    st.divider()

    st.header("Implemented Tools")
    st.write("- lookup_policy_tool")
    st.write("- search_similar_ticket_tool")
    st.write("- draft_acknowledgement_tool")
    st.write("- human_escalation_tool")

left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("Input Ticket")

    sample_tickets = {
        "Payment issue": "My payment was deducted but my order is not showing in the app.",
        "Account issue": "I cannot login because OTP is not coming on my phone.",
        "Technical issue": "The app keeps crashing whenever I try to upload a document.",
        "Delivery delay": "My service appointment was scheduled for yesterday but nobody came.",
        "Security issue": "I think my account is hacked and someone changed my email.",
        "General query": "Can you tell me the available plans and pricing?"
    }

    selected_sample = st.selectbox(
        "Use a sample ticket or write your own",
        ["Write my own"] + list(sample_tickets.keys())
    )

    default_text = ""
    if selected_sample != "Write my own":
        default_text = sample_tickets[selected_sample]

    ticket_text = st.text_area(
        "Ticket / complaint / request",
        value=default_text,
        height=180,
        placeholder="Example: My payment was deducted but the order is not confirmed."
    )

    st.subheader("Optional Metadata")

    customer_tier = st.selectbox(
        "Customer tier",
        ["standard", "premium", "enterprise"]
    )

    channel = st.selectbox(
        "Source channel",
        ["app", "email", "phone", "website", "whatsapp"]
    )

    previous_tickets = st.number_input(
        "Previous tickets from this user",
        min_value=0,
        max_value=20,
        value=0
    )

    metadata = {
        "customer_tier": customer_tier,
        "channel": channel,
        "previous_tickets": previous_tickets
    }

    run_button = st.button("Run Triage Agent", type="primary")

with right_col:
    st.subheader("Triage Output")

    if run_button:
        if not ticket_text.strip():
            st.error("Please enter a ticket before running the agent.")
        else:
            with st.spinner("Agent is analysing the ticket and calling tools..."):
                result = run_triage_agent(ticket_text=ticket_text, metadata=metadata)

            st.success("Triage completed")

            metric_col_1, metric_col_2, metric_col_3 = st.columns(3)

            with metric_col_1:
                st.metric("Category", result["category"].title())

            with metric_col_2:
                st.metric("Priority", result["priority"])

            with metric_col_3:
                st.metric("Confidence", f"{result['confidence']:.2f}")

            st.markdown("### Structured Output")

            structured_output = {
                "category": result["category"],
                "priority": result["priority"],
                "next_tool": result["next_tool"],
                "reasoning": result["reasoning"],
                "why": result["why"]
            }

            st.json(structured_output)

            st.markdown("### Why")
            st.write(result["why"])

            st.markdown("### Customer Acknowledgement Draft")

            acknowledgement = None
            for tool_result in result["tool_results"]:
                if tool_result["tool_name"] == "draft_acknowledgement_tool":
                    acknowledgement = tool_result["output"]["draft_message"]

            if acknowledgement:
                st.info(acknowledgement)

            st.markdown("### Tool Results")

            for tool_result in result["tool_results"]:
                with st.expander(tool_result["tool_name"], expanded=False):
                    st.json(tool_result)

            st.markdown("### Visible Reasoning Trace")
            show_reasoning_tree(result["reasoning_trace"])

            st.download_button(
                label="Download JSON Result",
                data=json.dumps(result, indent=2),
                file_name="triage_result.json",
                mime="application/json"
            )

    else:
        st.info("Enter a ticket and click **Run Triage Agent**.")