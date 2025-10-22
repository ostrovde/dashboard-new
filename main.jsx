import React, { Suspense } from 'react'
import ReactDOM from 'react-dom/client'
// import App from './App.jsx' // заменено на ленивый импорт ниже
import './index.css'
import ErrorBoundary from './components/ErrorBoundary.jsx'

// лениво загружаем App (код-сплит на будущее)
const App = React.lazy(() => import('./App.jsx'))

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <Suspense fallback={<div>Loading…</div>}>
        <App />
      </Suspense>
    </ErrorBoundary>
  </React.StrictMode>,
)
