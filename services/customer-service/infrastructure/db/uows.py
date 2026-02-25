from sqlalchemy.orm import Session

class UnitOfWork:
    def __init__(self, session_factory):
        """
        Initialise l'UoW avec une fabrique de sessions (sessionmaker).
        """
        self.session_factory = session_factory
        self.session: Session = None

    def __enter__(self):
        """
        Démarre la session de base de données quand on entre dans le bloc 'with'.
        """
        self.session = self.session_factory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Gère la fin du bloc 'with'. 
        Si une erreur est survenue (exc_type n'est pas None), on annule (rollback).
        Sinon, on valide les changements (commit).
        """
        if exc_type:
            # En cas d'exception, on annule tout ce qui a été fait dans la session
            self.session.rollback()
        else:
            # Si tout s'est bien passé, on enregistre définitivement en base
            self.session.commit()
        
        # On ferme systématiquement la connexion pour libérer les ressources
        self.session.close()