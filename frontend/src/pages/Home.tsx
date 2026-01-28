import Card from '../components/Card'

const Home = () => {
  return (
    <div className="home">
      <section className="hero">
        <div>
          <p className="eyebrow">Pour les agriculteurs et leurs partenaires</p>
          <h1>Une plateforme simple pour piloter vos projets agricoles.</h1>
          <p>
            AgroConnect vous aide à suivre vos demandes, coordonner les prestataires et garder un œil clair sur vos
            opérations. L&apos;interface reste simple et accessible pour tous les acteurs du terrain.
          </p>
          <div className="hero-actions">
            <button className="button button-primary">Découvrir l&apos;offre</button>
            <button className="button">Voir les dashboards</button>
          </div>
        </div>
        <Card title="Ce que vous obtenez">
          <ul>
            <li>Gestion des demandes en un seul endroit.</li>
            <li>Validation sécurisée via OTP pour les comptes.</li>
            <li>Trois dashboards dédiés: client, prestataire, admin.</li>
          </ul>
        </Card>
      </section>

      <section className="info-grid">
        <Card title="Client">
          <p>Suivez vos demandes, vos devis et vos interventions en temps réel.</p>
        </Card>
        <Card title="Prestataire">
          <p>Planifiez vos missions, confirmez vos disponibilités et communiquez avec les clients.</p>
        </Card>
        <Card title="Admin">
          <p>Supervisez l&apos;ensemble des activités, validez les profils et analysez les performances.</p>
        </Card>
      </section>
    </div>
  )
}

export default Home
