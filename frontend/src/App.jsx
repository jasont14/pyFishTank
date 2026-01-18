import { useState } from 'react'
import './App.css'
import TanksPage from './pages/TanksPage'
import FishPage from './pages/FishPage'
import MaintenancePage from './pages/MaintenancePage'
import ReportsPage from './pages/ReportsPage'

function App() {
  const [currentPage, setCurrentPage] = useState('tanks')

  const renderPage = () => {
    switch (currentPage) {
      case 'tanks':
        return <TanksPage />
      case 'fish':
        return <FishPage />
      case 'maintenance':
        return <MaintenancePage />
      case 'reports':
        return <ReportsPage />
      default:
        return <TanksPage />
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>pyFishTank</h1>
        <nav>
          <button
            className={currentPage === 'tanks' ? 'active' : ''}
            onClick={() => setCurrentPage('tanks')}
          >
            Tanks
          </button>
          <button
            className={currentPage === 'fish' ? 'active' : ''}
            onClick={() => setCurrentPage('fish')}
          >
            Fish
          </button>
          <button
            className={currentPage === 'maintenance' ? 'active' : ''}
            onClick={() => setCurrentPage('maintenance')}
          >
            Maintenance
          </button>
          <button
            className={currentPage === 'reports' ? 'active' : ''}
            onClick={() => setCurrentPage('reports')}
          >
            Reports
          </button>
        </nav>
      </aside>
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  )
}

export default App
