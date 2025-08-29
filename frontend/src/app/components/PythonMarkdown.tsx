import { Markdown } from "@copilotkit/react-ui";

export default function PythonMarkdown({ code }: { code: string }) {
  const markdownContent = "```python\n" + code + "\n```";

  return (
    <div>
      <Markdown content={markdownContent} />
    </div>
  );
}