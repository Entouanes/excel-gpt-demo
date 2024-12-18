import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import KernelArguments
from semantic_kernel.connectors.ai import PromptExecutionSettings
from semantic_kernel.prompt_template import InputVariable, PromptTemplateConfig

import os
from dotenv import load_dotenv

load_dotenv()


def azure_openai_settings_from_dot_env():
    deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    return deployment_name, api_key, endpoint


async def generate_summary(report, constraints=None):
    # Retrieve Azure OpenAI settings from the .env file
    deployment_name, api_key, endpoint = azure_openai_settings_from_dot_env()

    # Initialize the AzureChatCompletion service with the retrieved settings
    chat_completion_service = AzureChatCompletion(
        deployment_name=deployment_name,
        api_key=api_key,
        endpoint=endpoint,
        service_id="financial-report",
    )

    # Create a new semantic kernel instance
    kernel = sk.Kernel()
    # Add the chat completion service to the kernel
    kernel.add_service(chat_completion_service)

    # Prepare the arguments for the kernel invocation
    arguments = KernelArguments(
        report=report, 
        settings=PromptExecutionSettings(max_tokens=5000), 
        constraints=constraints
    )

    # Print the constraints for debugging purposes
    print(constraints)

    # Define the prompt for the financial report analysis
    analysis = """
        You are a financial analyst.
        You review financial reports and craft accurate executive summaries.
        Given the following report as a collection of tables in CSV format, craft a short summary.
        Your summary should be concise and informative.
        The executive summary should be no longer than 1 paragraphs and 500 words.
        The summary should be written in plain text, unless specified otherwise.
        If specified, take the following constraint into consideration: {{$constraints}}.
        Here is the collection of tables you should analyze: {{$report}}.
        """

    # Invoke the kernel with the analysis prompt to generate the summary
    summary = await kernel.invoke_prompt(
        function_name="sample_zero",
        plugin_name="sample_plugin",
        prompt=analysis,
        arguments=arguments,
    )

    # Invoke the kernel again to generate a title for the summary
    title = await kernel.invoke_prompt(
        function_name="sample_zero",
        plugin_name="sample_plugin",
        prompt="Find a catchy title for this report: {{$summary}}.",
        arguments=KernelArguments(
            summary=summary, 
            settings=PromptExecutionSettings(max_tokens=500)
        ),
    )

    return title.value[0].items[0].text, summary.value[0].items[0].text
