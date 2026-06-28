import pytest

from project_forge.ai_reasoning_engine import (
    AIContext,
    AzureOpenAIProvider,
    GovernmentHostedLLMProvider,
    ModelConfiguration,
    OfflineStubProvider,
    OpenAIProvider,
    PromptBuilder,
    PromptRegistry,
    PromptTemplate,
    PromptValidator,
    TemplateRegistry,
)
from project_forge.ai_reasoning_engine.models import ProviderType
from project_forge.context_engine import ContextBuilder
from project_forge.decision_engine import Decision, create_default_rules
from project_forge.decision_engine.models import DecisionContext
from project_forge.entity_engine import load_entities
from project_forge.event_engine import load_events
from project_forge.exercise_state import load_exercise_state
from project_forge.knowledge_engine import KnowledgeBaseLoader
from project_forge.scenario_engine import load_scenarios
from project_forge.translation_engine import (
    TranslationContext,
    TranslationPipeline,
    load_translation_dictionary,
)


def make_snapshot():
    exercise_state = load_exercise_state("config/exercise_state.example.yaml")
    scenario_registry = load_scenarios("config/scenario.example.yaml")
    entity_catalog = load_entities("config/entities.example.yaml")
    event_registry = load_events("config/events.example.yaml")
    knowledge_base = KnowledgeBaseLoader("knowledge_base").load()
    decision_context = DecisionContext(
        exercise_state=exercise_state,
        scenario=scenario_registry.get_current_scenario(),
        events=event_registry.events,
        entities=entity_catalog,
        training_objectives=["Validate EXCON decision rhythm"],
        escalation_rules=["Senior Controller approval required."],
    )
    decision_result = Decision(
        identifier="decision-ai",
        rules=create_default_rules(),
    ).execute(decision_context)
    return ContextBuilder(
        knowledge_base=knowledge_base,
        exercise_state=exercise_state,
        scenario_registry=scenario_registry,
        entity_catalog=entity_catalog,
        event_registry=event_registry,
        decision_results=[decision_result],
        training_objectives=["Validate EXCON decision rhythm"],
    ).build_current_context()


def make_template() -> PromptTemplate:
    return PromptTemplate(
        identifier="scenario-reasoning",
        version="1.0.0",
        system_prompt="You assist EXCON with notional scenario reasoning.",
        user_template=(
            "Use the deterministic context below.\n"
            "{context_summary}\n"
            "Instructions:\n"
            "{instructions}"
        ),
    )


def make_model_config() -> ModelConfiguration:
    return ModelConfiguration(
        provider_type=ProviderType.OFFLINE_STUB,
        model_name="offline-stub-model",
        temperature=0.0,
        max_tokens=500,
    )


def test_prompt_builder_creates_deterministic_ai_request() -> None:
    snapshot = make_snapshot()
    dictionary = load_translation_dictionary(
        "config/translation_dictionaries.example.yaml"
    ).get_dictionary("forge-example-translation")
    translation_result = TranslationPipeline(dictionary).translate(
        TranslationContext(
            text="Forge Example Exercise includes Host Nation and JTF HQ.",
            profile_identifier="exercise-products",
        )
    )
    ai_context = AIContext(
        context_snapshot=snapshot,
        translation_result=translation_result,
        instructions=["Preserve notional boundaries", "Do not generate reports"],
    )
    builder = PromptBuilder()

    first = builder.build_request(
        template=make_template(),
        ai_context=ai_context,
        model_configuration=make_model_config(),
    )
    second = builder.build_request(
        template=make_template(),
        ai_context=ai_context,
        model_configuration=make_model_config(),
    )

    assert first == second
    assert first.identifier == "scenario-reasoning:1.0.0:current"
    assert "Context Snapshot: current" in first.user_prompt
    assert "Translation Text: Exercise Iron Compass includes Asteria" in first.user_prompt
    assert "Do not generate reports" in first.user_prompt


def test_template_registry_supports_versions() -> None:
    old = PromptTemplate(
        identifier="reasoning",
        version="1.0.0",
        system_prompt="System",
        user_template="{context_summary}",
    )
    new = PromptTemplate(
        identifier="reasoning",
        version="1.1.0",
        system_prompt="System",
        user_template="{context_summary}",
    )
    registry = TemplateRegistry(templates=[new, old])

    assert registry.get_template("reasoning", "1.0.0") is old
    assert registry.get_template("reasoning") is new


def test_prompt_registry_validates_and_stores_requests() -> None:
    request = PromptBuilder().build_request(
        template=make_template(),
        ai_context=AIContext(context_snapshot=make_snapshot()),
        model_configuration=make_model_config(),
    )
    registry = PromptRegistry()

    registry.register_request(request)

    assert registry.get_request(request.identifier) is request


def test_offline_stub_provider_returns_valid_response_without_api_call() -> None:
    request = PromptBuilder().build_request(
        template=make_template(),
        ai_context=AIContext(context_snapshot=make_snapshot()),
        model_configuration=make_model_config(),
    )
    response = OfflineStubProvider(content="Stub reasoning complete.").generate(request)

    assert response.provider_type is ProviderType.OFFLINE_STUB
    assert response.content == "Stub reasoning complete."
    assert response.metadata == {"offline": True}


def test_live_provider_interfaces_do_not_call_apis() -> None:
    request = PromptBuilder().build_request(
        template=make_template(),
        ai_context=AIContext(context_snapshot=make_snapshot()),
        model_configuration=make_model_config(),
    )

    for provider in [OpenAIProvider(), AzureOpenAIProvider(), GovernmentHostedLLMProvider()]:
        with pytest.raises(NotImplementedError):
            provider.generate(request)


def test_prompt_validator_rejects_nondeterministic_temperature() -> None:
    request = PromptBuilder().build_request(
        template=make_template(),
        ai_context=AIContext(context_snapshot=make_snapshot()),
        model_configuration=make_model_config(),
    )
    bad_request = type(request)(
        identifier=request.identifier,
        prompt_template_id=request.prompt_template_id,
        prompt_template_version=request.prompt_template_version,
        system_prompt=request.system_prompt,
        user_prompt=request.user_prompt,
        model_configuration=ModelConfiguration(
            provider_type=ProviderType.OFFLINE_STUB,
            model_name="offline-stub-model",
            temperature=0.2,
        ),
    )

    with pytest.raises(ValueError):
        PromptValidator().validate_request(bad_request)


def test_prompt_template_requires_context_summary_placeholder() -> None:
    with pytest.raises(ValueError):
        PromptTemplate(
            identifier="bad-template",
            version="1.0.0",
            system_prompt="System",
            user_template="Missing placeholder",
        )
