from extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    first_name    = db.Column(db.String(50), nullable=False)
    last_name     = db.Column(db.String(50), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    student_id    = db.Column(db.String(50))
    phone         = db.Column(db.String(20))
    role          = db.Column(db.String(10), default='student')
    is_admin      = db.Column(db.Boolean, default=False)
    is_verified   = db.Column(db.Boolean, default=True)

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def create(first_name, last_name, email, student_id, phone, role, password_hash):
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            student_id=student_id,
            phone=phone,
            role=role,
            password_hash=password_hash
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def count_all():
        return User.query.count()


class Item(db.Model):
    __tablename__ = 'items'
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    category    = db.Column(db.String(50))
    status      = db.Column(db.String(20), default='lost')
    location    = db.Column(db.String(120))
    date_lost   = db.Column(db.String(20))
    image       = db.Column(db.String(200))
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def create(title, description, category, status, location, date_lost, image, user_id):
        item = Item(title=title, description=description, category=category,
                    status=status, location=location, date_lost=date_lost,
                    image=image, user_id=user_id)
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def get_all(status=None, category=None, search=None, page=1, per_page=12):
        query = Item.query
        if status:
            query = query.filter_by(status=status)
        if category:
            query = query.filter_by(category=category)
        if search:
            query = query.filter(Item.title.ilike(f'%{search}%'))
        return query.order_by(Item.id.desc()).paginate(page=page, per_page=per_page, error_out=False).items

    @staticmethod
    def get_by_id(item_id):
        return Item.query.get(item_id)

    @staticmethod
    def get_by_user(user_id):
        return Item.query.filter_by(user_id=user_id).order_by(Item.id.desc()).all()

    @staticmethod
    def update_status(item_id, status):
        item = Item.query.get(item_id)
        if item:
            item.status = status
            db.session.commit()

    @staticmethod
    def delete(item_id):
        item = Item.query.get(item_id)
        if item:
            db.session.delete(item)
            db.session.commit()

    @staticmethod
    def count_all():
        return Item.query.count()

    @staticmethod
    def count_by_status(status):
        return Item.query.filter_by(status=status).count()
    
    
class Match(db.Model):
    __tablename__ = 'matches'
    id            = db.Column(db.Integer, primary_key=True)
    lost_item_id  = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    found_item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    status        = db.Column(db.String(20), default='pending')  # pending, approved, rejected

    lost_item  = db.relationship('Item', foreign_keys=[lost_item_id])
    found_item = db.relationship('Item', foreign_keys=[found_item_id])

    @staticmethod
    def create(lost_item_id, found_item_id):
        match = Match(lost_item_id=lost_item_id, found_item_id=found_item_id)
        db.session.add(match)
        db.session.commit()
        return match

    @staticmethod
    def get_all():
        return Match.query.order_by(Match.id.desc()).all()

    @staticmethod
    def get_by_id(match_id):
        return Match.query.get(match_id)

    @staticmethod
    def update_status(match_id, status):
        match = Match.query.get(match_id)
        if match:
            match.status = status
            db.session.commit()

    @staticmethod
    def auto_match():
        lost_items  = Item.query.filter_by(status='lost').all()
        found_items = Item.query.filter_by(status='found').all()
        new_matches = 0
        for lost in lost_items:
            for found in found_items:
                already_exists = Match.query.filter_by(
                    lost_item_id=lost.id,
                    found_item_id=found.id
                ).first()
                if already_exists:
                    continue
                if lost.category == found.category:
                    import utils
                    is_ai_match = utils.evaluate_match_with_ai(lost, found)
                    if is_ai_match:
                        new_matches += 1
                        Match.create(lost.id, found.id)
                        
                        lost_user = User.query.get(lost.user_id)
                        if lost_user and lost_user.phone:
                            utils.send_alert(lost_user.phone, lost.title)
        return new_matches

    @staticmethod
    def count_pending():
        return Match.query.filter_by(status='pending').count()