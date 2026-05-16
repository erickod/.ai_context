from crewai import Crew, Process

from .agents import (
    daps_decomposer,
    daps_dependency_mapper,
    daps_lifecycle_mapper,
    daps_synthesizer,
    design_ddd_reviewer,
    engineer,
    perf_quality_reviewer,
    planner,
    review_synthesizer,
    security_reliability_reviewer,
    task_designer,
    test_analyst,
)
from .tasks import (
    cr_design_task,
    cr_perf_task,
    cr_security_task,
    cr_synthesis_task,
    daps_phase1_2_task,
    daps_phase3_task,
    daps_phase4_task,
    daps_phase5_task,
    engineering_task,
    planning_task,
    task_design_task,
    test_analysis_task,
)


class AIContextCrew:
    """
    State machine: TASK_DESIGN → PLANNING → TEST_ANALYSIS → ENGINEERING → CODE_REVIEW → DONE|BLOCKED

    CODE_REVIEW runs 3 specialist agents in parallel (design+DDD, security+reliability,
    perf+quality), then a synthesizer aggregates into the final verdict.

    DAPS lateral activation uses 4 agents: phases 1+2 sequential, then phases 3 and 4
    in parallel, then phase 5 synthesis.
    """

    def run(self, task_input: str) -> str:
        # ── Agents ──────────────────────────────────────────────────────────
        td_agent = task_designer()
        p_agent = planner()
        ta_agent = test_analyst()
        eng_agent = engineer()
        cr_design_agent = design_ddd_reviewer()
        cr_sec_agent = security_reliability_reviewer()
        cr_perf_agent = perf_quality_reviewer()
        cr_synth_agent = review_synthesizer()

        # ── Tasks ───────────────────────────────────────────────────────────
        td_task = task_design_task(td_agent, task_input)
        p_task = planning_task(p_agent)
        ta_task = test_analysis_task(ta_agent)
        eng_task = engineering_task(eng_agent)

        # Code review — 3 async specialists + 1 synthesizer
        review_design = cr_design_task(cr_design_agent)
        review_sec = cr_security_task(cr_sec_agent)
        review_perf = cr_perf_task(cr_perf_agent)
        review_synth = cr_synthesis_task(cr_synth_agent)

        # ── Context wiring ───────────────────────────────────────────────────
        p_task.context = [td_task]
        ta_task.context = [td_task, p_task]
        eng_task.context = [td_task, p_task, ta_task]

        # All 3 reviewers read the engineering output independently
        review_design.context = [eng_task]
        review_sec.context = [eng_task]
        review_perf.context = [eng_task]

        # Synthesizer waits for all 3 async reviewers to complete
        review_synth.context = [review_design, review_sec, review_perf]

        # ── Crew ─────────────────────────────────────────────────────────────
        crew = Crew(
            agents=[
                td_agent, p_agent, ta_agent, eng_agent,
                cr_design_agent, cr_sec_agent, cr_perf_agent, cr_synth_agent,
            ],
            tasks=[
                td_task, p_task, ta_task, eng_task,
                review_design, review_sec, review_perf,  # run in parallel
                review_synth,                             # waits for above 3
            ],
            process=Process.sequential,
            verbose=True,
        )

        return str(crew.kickoff(inputs={"task_input": task_input}))

    def run_daps(self, scope: str) -> str:
        """
        Lateral DAPS activation for structural/architectural analysis.
        Does not change STATE.

        Phases 1+2 run sequentially, then phases 3 and 4 run in parallel,
        then phase 5 synthesizes the PropostaDeDesign.
        """
        decomposer = daps_decomposer()
        dep_mapper = daps_dependency_mapper()
        life_mapper = daps_lifecycle_mapper()
        synthesizer = daps_synthesizer()

        p1_2 = daps_phase1_2_task(decomposer, scope)
        p3 = daps_phase3_task(dep_mapper)   # async
        p4 = daps_phase4_task(life_mapper)  # async
        p5 = daps_phase5_task(synthesizer)

        # Phase 3 and 4 both read from phase 1+2 output; run in parallel
        p3.context = [p1_2]
        p4.context = [p1_2]

        # Phase 5 waits for both parallel phases to complete
        p5.context = [p3, p4]

        crew = Crew(
            agents=[decomposer, dep_mapper, life_mapper, synthesizer],
            tasks=[p1_2, p3, p4, p5],  # p3 and p4 run in parallel after p1_2
            process=Process.sequential,
            verbose=True,
        )

        return str(crew.kickoff(inputs={"scope": scope}))
