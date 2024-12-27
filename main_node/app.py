from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
import os

# Конфигурация приложения и базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/main_db")

# Инициализация базы данных
engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 10})
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Flask приложение
app = Flask(__name__)

# Определение модели базы данных
class Node(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)
    resources = Column(JSON, nullable=True)

# Создание таблиц
Base.metadata.create_all(engine)

# Маршруты API
@app.route('/register', methods=['POST'])
def register_node():
    """
    Регистрация или обновление информации о ноде.
    """
    data = request.json
    node_id = data.get('node_id')
    status = data.get('status', 'unknown')
    resources = data.get('resources', {})

    if not node_id:
        return jsonify({"error": "node_id is required"}), 400

    session = Session()
    try:
        # Проверка на существующий нод
        existing_node = session.query(Node).filter_by(node_id=node_id).first()
        if existing_node:
            existing_node.status = status
            existing_node.resources = resources
            message = "Node updated successfully"
        else:
            # Создание нового нода
            node = Node(node_id=node_id, status=status, resources=resources)
            session.add(node)
            message = "Node registered successfully"

        session.commit()
        return jsonify({"message": message}), 200
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/nodes', methods=['GET'])
def list_nodes():
    """
    Список всех зарегистрированных нодов.
    """
    session = Session()
    try:
        nodes = session.query(Node).all()
        return render_template('nodes.html', nodes=nodes)
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# Главная точка входа
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
