export default function ResultsDisplay({ result }) {
  return (
    <div className="results-section">
      <div className="answer-box">
        <h3>Answer</h3>
        <p>{result.answer}</p>
        <div className="confidence">
          Confidence: {(result.confidence * 100).toFixed(0)}%
        </div>
      </div>

      <div className="sources-box">
        <h3>Sources</h3>
        {result.sources &&
          result.sources.map((source, idx) => (
            <div key={idx} className="source">
              <strong>{source.source_doc}</strong>
              <p>{source.chunk_text.substring(0, 200)}...</p>
            </div>
          ))}
      </div>

      <div className="timing">Response time: {result.response_time_ms}ms</div>
    </div>
  )
}
