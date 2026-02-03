import { useEffect, useState } from "react";

const STATUS = {
  loading: "loading",
  ok: "ok",
  error: "error"
};

function App() {
  const [apiStatus, setApiStatus] = useState({
    state: STATUS.loading,
    message: "Checking backend..."
  });

  useEffect(() => {
    let isActive = true;

    fetch("/api/health")
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`Request failed: ${response.status}`);
        }
        const data = await response.json();
        return data?.status === "ok"
          ? "Backend is healthy."
          : "Backend responded, but status is unexpected.";
      })
      .then((message) => {
        if (!isActive) return;
        setApiStatus({ state: STATUS.ok, message });
      })
      .catch((error) => {
        if (!isActive) return;
        setApiStatus({
          state: STATUS.error,
          message: error.message || "Unable to reach backend."
        });
      });

    return () => {
      isActive = false;
    };
  }, []);

  return (
    <div className="page">
      <header className="header">
        <h1>Basketball Fantasy Helper</h1>
        <p>One-page React frontend</p>
      </header>

      <main className="content">
        <section className="card">
          <h2>Backend Status</h2>
          <p className={`status status-${apiStatus.state}`}>
            {apiStatus.message}
          </p>
        </section>
      </main>

      <footer className="footer">
        <small>© 2026</small>
      </footer>
    </div>
  );
}

export default App;
