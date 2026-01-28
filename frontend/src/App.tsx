
import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import RoleRoute from './components/RoleRoute'
import AdminDashboard from './pages/dashboards/AdminDashboard'
import ClientDashboard from './pages/dashboards/ClientDashboard'
import PrestataireDashboard from './pages/dashboards/PrestataireDashboard'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Settings from './pages/Settings'
import './App.css'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/dashboard/client"
          element={
            <ProtectedRoute>
              <RoleRoute allowedRole="CLIENT">
                <ClientDashboard />
              </RoleRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard/prestataire"
          element={
            <ProtectedRoute>
              <RoleRoute allowedRole="PRESTATAIRE">
                <PrestataireDashboard />
              </RoleRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard/admin"
          element={
            <ProtectedRoute>
              <RoleRoute allowedRole="ADMIN">
                <AdminDashboard />
              </RoleRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>

  )
}

export default App
