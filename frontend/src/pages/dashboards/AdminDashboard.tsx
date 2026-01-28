import Card from '../../components/Card'
import DashboardShell from '../../components/DashboardShell'

const AdminDashboard = () => {
  return (
    <DashboardShell title="Dashboard Administrateur" subtitle="Supervision globale des comptes et activités.">
      <div className="grid-columns">
        <Card title="Validation des profils">
          <p>Validez les comptes et suivez les justificatifs soumis.</p>
        </Card>
        <Card title="Performance">
          <p>Analysez les demandes, interventions et temps de réponse.</p>
        </Card>
        <Card title="Support">
          <p>Centralisez les retours et les besoins des utilisateurs.</p>
        </Card>
      </div>
    </DashboardShell>
  )
}

export default AdminDashboard
