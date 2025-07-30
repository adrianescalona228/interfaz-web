from flask import Blueprint, request, flash, render_template, jsonify
import logging
from database import db
from database.models import Sale, Debt, Inventory, Product, SaleItem

sales_history_bp = Blueprint("sales_history", __name__)

@sales_history_bp.route("/sales_history")
def sales_history():
    sales = db.session.query(Sale).order_by(Sale.sale_number).all()

    grouped_sales = []
    for sale in sales:
        sale_data = {
            "sale_number": sale.sale_number,
            "client_name": sale.client.client_name,
            "issue_date": sale.issue_date.strftime("%d-%m-%Y") if sale.issue_date else "N/A",
            "due_date": sale.due_date.strftime("%d-%m-%Y") if sale.due_date else "N/A",
            "products": [],
            "paid_amount": sale.debt.paid_amount if sale.debt else 0.0,
            "status": sale.debt.status if sale.debt else "unknown",
        }

        total = 0.0
        for item in sale.items:
            product_name = item.product.name if item.product else "Unknown Product"
            quantity = float(item.quantity or 0)
            price = float(item.price_unit or 0)
            total = sale.total_amount

            sale_data["products"].append({
                "product": product_name,
                "quantity": quantity,
                "price": price,
            })

        sale_data["total_amount"] = total
        print(f"Total amount: {sale_data["total_amount"]}", flush=True)
        grouped_sales.append(sale_data)

    return render_template("sales/sales_history.html", sales=grouped_sales)

@sales_history_bp.route('/delete_sale/<int:sale_number>', methods=['POST'])
def delete_sale(sale_number):
    logger = logging.getLogger(__name__)

    try:
        sale = db.session.query(Sale).filter_by(sale_number=sale_number).first()

        if not sale:
            logger.error(f"Sale with number {sale_number} not found.")
            flash("Sale not found", "error")
            return '', 404

        logger.info(f"Attempting to delete sale #{sale_number}")

        # Get related debt
        debt = sale.debt
        client = sale.client
        paid_amount = debt.paid_amount if debt else 0.0
        total_amount = sale.total_amount if debt else 0.0

        # Guardar detalles antes de eliminar
        items = list(sale.items)  # mantener referencia antes de borrar
        product_adjustments = []

        for item in items:
            product = item.product
            if not product:
                continue

            # Obtener entrada de inventario correspondiente
            inventory = db.session.query(Inventory).filter_by(product_id=product.id).first()
            if inventory:
                inventory.quantity += item.quantity
                product_adjustments.append((product.name, item.quantity))

        # Eliminar la venta (cascade debería eliminar sale_items si está configurado)
        db.session.delete(sale)
        logger.info(f"Sale #{sale_number} deleted.")

        # Eliminar la deuda asociada
        if debt:
            db.session.delete(debt)
            logger.info(f"Debt for sale #{sale_number} deleted.")

        db.session.commit()
        flash("Sale and related data deleted successfully", "success")

        for name, quantity in product_adjustments:
            logger.info(f"Restored {quantity} units to inventory for product '{name}'")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting sale #{sale_number}: {e}")
        flash("An error occurred while deleting the sale", "error")
        return '', 500

    return '', 200

@sales_history_bp.route('/remove_product/<int:sale_number>/<int:sale_item_id>', methods=['POST'])
def remove_product(sale_number, sale_item_id):
    try:
        sale = db.session.query(Sale).filter_by(sale_number=sale_number).first()
        if not sale:
            return jsonify({"error": "Sale not found"}), 404

        sale_item = db.session.get(SaleItem, sale_item_id)
        if not sale_item or sale_item.sale_id != sale.id:
            return jsonify({"error": "Sale item not found for this sale"}), 404

        # Update inventory: devolver cantidad del sale_item eliminado
        inventory = db.session.query(Inventory).filter_by(product_id=sale_item.product_id).first()
        if inventory:
            inventory.quantity += sale_item.quantity

        # Reducir total_amount en Sale
        amount_to_reduce = sale_item.quantity * sale_item.price_unit
        sale.total_amount -= amount_to_reduce

        # Borrar el sale_item
        db.session.delete(sale_item)

        # Si ya no hay más items en la venta, eliminar sale y deuda
        remaining_items = db.session.query(SaleItem).filter_by(sale_id=sale.id).count()
        if remaining_items == 0:
            debt = db.session.query(Debt).filter_by(sale_id=sale.id).first()
            if debt:
                db.session.delete(debt)
            db.session.delete(sale)
        else:
            # Si queda deuda, tal vez actualizarla o dejarla
            pass

        db.session.commit()
        return jsonify({"message": "Product removed from sale successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error removing product from sale"}), 500

@sales_history_bp.route('/update_paid_amount', methods=['POST'])
def update_paid_amount():
    logger = logging.getLogger(__name__)

    try:
        data = request.get_json()
        sale_number = data.get('sale_number')
        paid_amount = data.get('paid_amount')

        # Basic validation
        if not sale_number or not isinstance(sale_number, int):
            logger.error(f"Invalid sale number: {sale_number}")
            return jsonify({'success': False, 'message': 'Invalid sale number'}), 400

        if not isinstance(paid_amount, (int, float)):
            logger.error(f"Invalid paid amount: {paid_amount}")
            return jsonify({'success': False, 'message': 'Invalid paid amount'}), 400

        paid_amount = float(paid_amount)

        # Query the sale by sale_number
        sale = db.session.query(Sale).filter_by(sale_number=sale_number).first()
        if not sale:
            logger.error(f"Sale not found with number: {sale_number}")
            return jsonify({'success': False, 'message': 'Sale not found'}), 404

        # Query associated debt (1-to-1)
        debt = db.session.query(Debt).filter_by(sale_id=sale.id).first()
        if not debt:
            logger.error(f"No associated debt found for sale number: {sale_number}")
            return jsonify({'success': False, 'message': 'Debt not found for the sale'}), 404

        # Update paid amount
        debt.paid_amount = paid_amount
        # Optionally update debt status here if needed

        db.session.commit()
        logger.info(f"Paid amount updated for sale #{sale_number}: {paid_amount}")

        return jsonify({
            'success': True,
            'message': 'Paid amount updated successfully',
            'new_paid_amount': paid_amount
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating paid amount: {e}")
        return jsonify({'success': False, 'message': f'Error updating paid amount: {str(e)}'}), 500



















#
#@sales_history_bp.route('/generar_nota_entrega', methods=['POST'])
#def generar_nota_entrega():
#    try:
#        data = request.json
#        numero_venta = data.get('numero_venta')
#
#        datos_cliente = obtener_datos_cliente_y_venta(numero_venta)
#        if not datos_cliente:
#            logging.error('Cliente o venta no encontrado para el número de venta: %s', numero_venta)
#            return jsonify({'mensaje': 'Cliente o venta no encontrado'}), 404
#
#        ruta_nota = crear_nota_entrega(datos_cliente)
#        return jsonify({"message": "Nota de entrega generada", "ruta": ruta_nota}), 200
#
#    except Exception as e:
#        logging.error('Error al generar la nota de entrega: %s', e, exc_info=True)
#        return jsonify({'error': 'Error interno del servidor'}), 500
#
#def abrir_libro_excel(ruta_archivo):
#    try:
#        return load_workbook(ruta_archivo)
#    except Exception as e:
#        logging.error('Error al abrir el libro de Excel: %s', e, exc_info=True)
#        raise
#
#def obtener_datos_cliente_y_venta(numero_venta):
#    db = get_db()
#    cursor = db.cursor()
#
#    try:
#        cursor.execute("SELECT cliente FROM Ventas WHERE numero_venta = ?", (numero_venta,))
#        cliente = cursor.fetchone()
#        if not cliente:
#            return None
#        
#        nombre_cliente = cliente[0]
#
#        cursor.execute("SELECT razon_social, rif_cedula, direccion, telefono FROM Clientes WHERE nombre_cliente = ?", (nombre_cliente,))
#        cliente = cursor.fetchone()
#        if not cliente:
#            return None
#        
#        razon_social, rif_cedula, direccion, telefono = cliente
#        
#        cursor.execute("SELECT numero_venta, producto, cantidad, precio, fecha FROM Ventas WHERE numero_venta = ?", (numero_venta,))
#        productos = cursor.fetchall()  # Obtener todas las ventas asociadas
#
#        if productos:
#            ventas_list = [
#                {
#                    'numero_venta': producto[0],
#                    'producto': producto[1].strip(),
#                    'cantidad': producto[2],
#                    'precio': producto[3],
#                    'fecha': producto[4]
#                }
#                for producto in productos
#            ]
#
#            return {
#                'nombre_cliente': nombre_cliente.strip(),
#                'razon_social': razon_social.strip(),
#                'rif_cedula': rif_cedula.strip(),
#                'direccion': direccion.strip(),
#                'telefono': telefono.strip(),
#                'ventas': ventas_list
#            }
#        else:
#            return {'error': 'No se encontró la venta'}
#
#    except Exception as e:
#        logging.error('Error al obtener datos del cliente y la venta: %s', e, exc_info=True)
#        raise
#    finally:
#        db.close()
#
#def insertar_direccion(sheet, direccion, fila_inicial):
#    try:
#        ancho_maximo = 80
#
#        if len(direccion) > ancho_maximo:
#            punto_corte = direccion.rfind(' ', 0, ancho_maximo)
#            if punto_corte == -1:
#                punto_corte = ancho_maximo
#
#            direccion_1 = direccion[:punto_corte]
#            direccion_2 = direccion[punto_corte + 1:]
#
#            rango_celda_1 = sheet.Cells(fila_inicial, 6).MergeArea
#            rango_celda_1.Cells(1, 1).Value = direccion_1
#
#            rango_celda_2 = sheet.Cells(fila_inicial + 1, 6).MergeArea
#            rango_celda_2.Cells(1, 1).Value = direccion_2
#        else:
#            rango_celda_1 = sheet.Cells(fila_inicial, 6).MergeArea
#            rango_celda_1.Cells(1, 1).Value = direccion
#    except Exception as e:
#        logging.error('Error al insertar dirección en la hoja de Excel: %s', e, exc_info=True)
#        raise
#
#def crear_nota_entrega(datos_cliente):
#    logging.info("Iniciando la creación de la nota de entrega...")
#
#    ruta_plantilla, ruta_guardar = config_global()
#
#    try:
#        pythoncom.CoInitialize()
#        logging.info("COM de Python inicializada correctamente.")
#
#        if not os.path.exists(ruta_plantilla):
#            raise FileNotFoundError(f"La plantilla no se encontró en la ruta: {ruta_plantilla}")
#
#        try:
#            excel = win32.DispatchEx('Excel.Application')
#            logging.info("Excel iniciado correctamente.")
#        except Exception as e:
#            logging.error('Error al iniciar Excel: %s', e, exc_info=True)
#            raise
#
#        if excel is None:
#            raise RuntimeError("No se pudo iniciar Excel. Asegúrate de que esté instalado correctamente.")
#
#        try:
#            workbook = excel.Workbooks.Open(ruta_plantilla)
#            logging.info("Plantilla de Excel abierta correctamente.")
#        except Exception as e:
#            logging.error('Error al abrir la plantilla de Excel: %s', e, exc_info=True)
#            raise
#
#        try:
#            sheet = workbook.ActiveSheet
#            logging.info("Hoja activa seleccionada correctamente.")
#
#            sheet.Cells(3, 9).Value = datos_cliente['razon_social']
#            sheet.Cells(3, 29).Value = datos_cliente['rif_cedula']
#            logging.info("Datos del cliente (razón social y RIF/Cédula) insertados correctamente.")
#            
#            insertar_direccion(sheet, datos_cliente['direccion'], 5)
#            logging.info("Dirección del cliente insertada correctamente.")
#            
#            sheet.Cells(7, 29).Value = datos_cliente['telefono']
#            logging.info("Teléfono del cliente insertado correctamente.")
#
#            if datos_cliente['ventas']:
#                primer_producto = datos_cliente['ventas'][0]
#                sheet.Cells(7, 7).Value = primer_producto['fecha']
#                sheet.Cells(1, 32).Value = primer_producto['numero_venta']
#
#            fila_inicio = 12
#            for producto in datos_cliente['ventas']:
#                sheet.Cells(fila_inicio, 1).Value = producto['cantidad']
#                sheet.Cells(fila_inicio, 4).Value = producto['producto']
#                sheet.Cells(fila_inicio, 25).Value = producto['precio']
#                fila_inicio += 1
#            logging.info("Datos de todos los productos insertados correctamente.")
#
#        except Exception as e:
#            logging.error('Error al modificar la hoja activa: %s', e, exc_info=True)
#            raise
#
#        try:
#            nombre_archivo = f"NDE.{primer_producto['numero_venta']}_{datos_cliente['nombre_cliente']}.xlsx"
#            ruta_completa = os.path.join(ruta_guardar, nombre_archivo)
#            workbook.SaveAs(ruta_completa)
#            workbook.Close()
#            logging.info("Archivo guardado correctamente en: %s", ruta_completa)
#        except Exception as e:
#            logging.error('Error al guardar el archivo: %s', e, exc_info=True)
#            raise
#
#        try:
#            os.startfile(ruta_completa)
#            logging.info("Archivo %s abierto correctamente.", nombre_archivo)
#        except Exception as e:
#            logging.error('Error al abrir el archivo guardado: %s', e, exc_info=True)
#            raise
#
#        logging.info("Proceso de creación de la nota de entrega completado.")
#        return ruta_completa
#
#    except Exception as e:
#        logging.error('Se encontró un error: %s', e, exc_info=True)
#        raise
