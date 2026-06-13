const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col gap-4 px-6 py-16">
      <h1 className="text-3xl font-bold">FastAPI + Next.js Template</h1>
      <p className="text-slate-700">このテンプレートはバックエンドとフロントエンドを分離した構成です。</p>
      <div className="rounded-lg border border-slate-200 bg-white p-4">
        <p className="font-medium">Backend API URL</p>
        <code className="mt-2 block rounded bg-slate-100 p-2 text-sm">{apiBaseUrl}</code>
      </div>
      <p className="text-sm text-slate-600">
        API クライアントは <code>yarn gen</code> で <code>src/gen/</code> に生成されます。
      </p>
    </main>
  );
}
