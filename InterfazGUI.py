import streamlit as st
import pandas as pd

# Configuración inicial
st.set_page_config(page_title="Gestión de Línea de Producción", layout="wide")

# Capacidad máxima de producción
production_capacity = 500

# Inicialización de datos
if "orders" not in st.session_state:
    st.session_state.orders = pd.DataFrame(
        columns=["ID Pedido", "Cliente", "Producto", "Demanda", "Importancia", "Prioridad"]
    )
    st.session_state.next_order_id = 1
    st.session_state.remaining_capacity = production_capacity


def calculate_priorities():
    """Calcula las prioridades heurísticas para los pedidos."""
    if not st.session_state.orders.empty:
        st.session_state.orders["Prioridad"] = (
            st.session_state.orders["Importancia"] / st.session_state.orders["Demanda"]
            + 1 / (production_capacity - st.session_state.orders["Demanda"])
        )
        st.session_state.orders.sort_values("Prioridad", ascending=False, inplace=True)


def add_order(client, product, demand, importance):
    """Agrega un nuevo pedido y actualiza los cálculos."""
    global production_capacity

    if demand > st.session_state.remaining_capacity:
        st.warning("La demanda excede la capacidad restante.")
        return

    # Crear el nuevo pedido
    new_order = pd.DataFrame(
        [[st.session_state.next_order_id, client, product, demand, importance, 0]],
        columns=st.session_state.orders.columns,
    )

    # Agregar pedido al DataFrame y actualizar estado
    st.session_state.orders = pd.concat([st.session_state.orders, new_order], ignore_index=True)
    st.session_state.next_order_id += 1
    st.session_state.remaining_capacity -= demand

    calculate_priorities()
    st.success(f"Pedido agregado exitosamente (ID: {st.session_state.next_order_id - 1}).")


def remove_order(order_id):
    """Elimina un pedido por su ID y ajusta la capacidad restante."""
    global production_capacity

    # Verificar si el pedido existe
    if order_id not in st.session_state.orders["ID Pedido"].values:
        st.warning("El ID del pedido no existe.")
        return

    # Recuperar la demanda del pedido eliminado
    demand = st.session_state.orders.loc[st.session_state.orders["ID Pedido"] == order_id, "Demanda"].values[0]
    st.session_state.remaining_capacity += demand

    # Eliminar el pedido
    st.session_state.orders = st.session_state.orders[st.session_state.orders["ID Pedido"] != order_id]

    calculate_priorities()
    st.success(f"Pedido eliminado exitosamente (ID: {order_id}).")


# Layout de la aplicación
st.title("Gestión de Línea de Producción")
st.sidebar.title("Acciones")

# Mostrar capacidad restante
st.sidebar.metric("Capacidad restante", st.session_state.remaining_capacity)

# Formulario para agregar un nuevo pedido
with st.sidebar.form("add_order_form"):
    st.subheader("Agregar Pedido")
    client = st.text_input("Cliente", key="add_client")
    product = st.text_input("Producto", key="add_product")
    demand = st.number_input("Demanda", min_value=1, max_value=production_capacity, key="add_demand")
    importance = st.slider("Importancia del Cliente", min_value=1, max_value=10, key="add_importance")
    submitted = st.form_submit_button("Agregar Pedido")

    if submitted:
        if client and product:
            add_order(client, product, demand, importance)
        else:
            st.warning("Por favor, completa todos los campos.")

# Formulario para eliminar un pedido
with st.sidebar.form("remove_order_form"):
    st.subheader("Dar de Baja Pedido")
    order_id = st.number_input("ID del Pedido", min_value=1, step=1, key="remove_order_id")
    remove_submitted = st.form_submit_button("Eliminar Pedido")

    if remove_submitted:
        remove_order(order_id)

# Mostrar tabla de pedidos
st.subheader("Pedidos Actuales")
if st.session_state.orders.empty:
    st.info("No hay pedidos registrados.")
else:
    st.dataframe(st.session_state.orders)
