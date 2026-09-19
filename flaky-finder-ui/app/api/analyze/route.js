export const maxDuration = 60;

const MAX_CHARS = 200_000;

function extractText(data) {
  const out = data?.outputs?.[0]?.outputs?.[0];
  return (
    out?.results?.message?.text ??
    out?.outputs?.message?.message ??
    out?.artifacts?.message ??
    null
  );
}

export async function POST(request) {
  const {
    LANGFLOW_URL,
    LANGFLOW_API_KEY,
    LANGFLOW_FLOW = "flaky-finder",
    PROMPT_NODE = "Prompt Template",
    APP_PASSWORD,
  } = process.env;

  if (!LANGFLOW_URL || !LANGFLOW_API_KEY) {
    return Response.json({ error: "Server is missing LANGFLOW_URL or LANGFLOW_API_KEY." }, { status: 500 });
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "Request body must be JSON." }, { status: 400 });
  }

  if (APP_PASSWORD && body.password !== APP_PASSWORD) {
    return Response.json({ error: "Wrong password." }, { status: 401 });
  }

  const { run1, run2 } = body;
  const prompt = typeof body.prompt === "string" && body.prompt.trim() ? body.prompt.trim() : "find flaky tests";
  if (typeof run1 !== "string" || typeof run2 !== "string" || !run1 || !run2) {
    return Response.json({ error: "Both run1 and run2 are required." }, { status: 400 });
  }
  if (run1.length > MAX_CHARS || run2.length > MAX_CHARS) {
    return Response.json({ error: "Each file must be under 200,000 characters." }, { status: 413 });
  }

  const url = `${LANGFLOW_URL.replace(/\/$/, "")}/api/v1/run/${encodeURIComponent(LANGFLOW_FLOW)}`;
  let res;
  try {
    res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-api-key": LANGFLOW_API_KEY },
      body: JSON.stringify({
        input_value: prompt,
        input_type: "chat",
        output_type: "chat",
        tweaks: { [PROMPT_NODE]: { test_data: `${run1}\n\n${run2}` } },
      }),
    });
  } catch (e) {
    return Response.json({ error: `Could not reach Langflow: ${e.message}` }, { status: 502 });
  }

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    return Response.json(
      { error: `Langflow returned ${res.status}.`, detail: data?.detail ?? null },
      { status: 502 }
    );
  }

  const result = extractText(data);
  if (!result) {
    return Response.json({ error: "Langflow responded, but no message text was found." }, { status: 502 });
  }
  return Response.json({ result });
}
