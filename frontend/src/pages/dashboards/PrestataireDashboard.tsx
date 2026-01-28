import Card from '../../components/Card'
import DashboardShell from '../../components/DashboardShell'

const PrestataireDashboard = () => {
  return (
    <DashboardShell title="Dashboard Prestataire" subtitle="Organisez vos missions et votre planning.">
      <div className="grid-columns">
        <Card title="Missions assignées">
          <p>Visualisez les interventions du jour et confirmez vos disponibilités.</p>
        </Card>
        <Card title="Revenus">
          <p>Consultez vos paiements en attente et vos gains mensuels.</p>
        </Card>
        <Card title="Messages">
          <p>Restez en contact avec les clients et l&apos;administration.</p>
        </Card>
      </div>
    </DashboardShell>
  )
}

export default PrestataireDashboard
