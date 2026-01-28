import Card from '../../components/Card'
import DashboardShell from '../../components/DashboardShell'

const ClientDashboard = () => {
  return (
    <DashboardShell title="Dashboard Client" subtitle="Suivi clair de vos demandes agricoles.">
      <div className="grid-columns">
        <Card title="Demandes en cours">
          <p>Consultez les interventions en attente et suivez les réponses des prestataires.</p>
        </Card>
        <Card title="Historique">
          <p>Gardez une trace des travaux réalisés et des devis acceptés.</p>
        </Card>
        <Card title="Documents">
          <p>Téléchargez vos factures et confirmations depuis un seul endroit.</p>
        </Card>
      </div>
    </DashboardShell>
  )
}

export default ClientDashboard
