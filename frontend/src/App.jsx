import { RankingCursos } from './components/RankingCursos'
import './App.css'

function App() {
  return (
    <main className="app-shell">
      <header className="page-header">
        <p className="eyebrow">Mini Portfólio</p>
        <h1>Ranking de cursos</h1>
        <p className="page-description">
          Acompanhe o desempenho dos cursos a partir do score calculado pela API.
        </p>
      </header>
      <RankingCursos />
    </main>
  )
}

export default App
