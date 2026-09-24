const STREAMLIT_BASE = 'http://localhost:8501'

// Shared Streamlit embed page component
export default function StreamlitPage({ title, description, path, height = 800 }) {
  return (
    <div>
      <div className="page-header">
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      <div className="sl-iframe-wrapper">
        <iframe
          src={`${STREAMLIT_BASE}/${path}`}
          height={height}
          title={title}
          allow="microphone"
        />
      </div>
    </div>
  )
}
