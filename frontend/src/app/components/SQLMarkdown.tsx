import { Markdown } from "@copilotkit/react-ui";

export default function SQLMarkdown({ query }: { query: string }) {
  const markdownContent = "```sql\n" + query + "\n```";

  return (
    <div>
      <Markdown content={markdownContent} />
    </div>
  );
}