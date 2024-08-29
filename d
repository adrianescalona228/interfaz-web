[33m4cb913e[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mmaster[m[33m, [m[1;31morigin/master[m[33m, [m[1;31morigin/HEAD[m[33m)[m ver deudas ahora es editable. agregue un roll back para asegurarnos de no perder datos por accidente. el backend funciona correctamente
[33md61ac51[m ahora si
[33m30af94e[m ahora siii, ya hare merge en master
[33ma953447[m arreglados los cambios de la logica de compras para que se actualice correctamente el inventario al agregar y eliminar compras
[33m1ecff4a[m arreglada la logica de compras y eliminar compras, por ahora todo funciona correctamente
[33m01131b9[m Eliminar archivos .pyc del repositorio
[33m71dda2a[m nueva funcionalidad: agregar una entrada nueva de producto al inventario
[33m4f8d777[m arreglado bug en carrito de compras que no aceptaba cantidad en decimal
[33m338315f[m ahora si vamos a empezar a usar el programa
[33m8043eaa[m Stop tracking DATABASE/inventory2.db
[33meb64c8a[m arreglado buscador inventario
[33m61ac522[m estoy adaptando la pagina para telefonos. llevo el index y el inventario. todavia tengo que ajustar cosas del inventario
[33m043decf[m interfaz web master 1.0
[33me6300a6[m interfaz web fase desarrollo 1.0
[33m30b846d[m Esta es la version que hare merge en master, ya la pagina se empezara a usar en produccion para ver errores y corregir
[33md32121b[m Ya termine con la logica de compras, falta agregar un producto nuevo, pero lo hago luego, voy a hacer la logica de clientes
[33m5194f3e[m cambie todos los ajax por fetch en la pagina de registro_ventas.js
[33m3e4ce2d[m Agregue un filtro en historial ventas. el css ya esta mucho mejor logrado. quiero agregar un filtro de facturas vencidas
[33m857a44c[m estoy acomodando el css de la pagina, no he hecho lo de agregar un nuevo cliente
[33m8ca9a90[m Ya estructure todo el codigo y parece funcionar correctamente
[33m8190815[m aun no he creado la logica para agregar el nuevo cliente, pero primero voy a reestructurar la pagina completa porque ahorita esta todo muy desorganizado. ya cree el html de agregar nuevo cliente
[33mcda147d[m Cambie la logica de las ventas por completo. Actualmente se envia una sola solicitud desde el front al back con toda la informacion en un array y en el back se desglosa con un bucle for. Por ahora parece funcionar correctamente todo el tema de las tablas de ventas, facturas y deudas, espero que se mantenga asi. lo dejare asi por ahora, manana vuelvo a probar
[33mbfd6089[m Por ahora la tabla de deudas y facturas parecen funcionar correctamente. tengo que hacer pruebas exhaustivas a ver si consigo errores. guardo este commit como punto seguro
[33m7febe0f[m ya funciona el prototipo de eliminar productos y ventas y que se rebaje a la deuda total del cliente y que se rebaje en la factura de la venta o que se elimine como tal. aun tengo que hacer pruebas al respecto, pero lo dejare asi por ahora. ahora tengo que crear la logica para el sistema de abonos
[33m7a82447[m hago este commit pa hacer un checkpoint. cree la tabla de deudas, voy a hacer que esa tabla se actualice cada vez que se registra una venta
[33m9e5b6a7[m Ya agregue el autocompletado en la pagina de abonos, por ahora creo que todo funcion correctamente.
[33m519483f[m Agregue la pagina para ver las deudas totales de los clientes, aun no muestra nada. tambien cree la tabla de las facturas. las facturas se registran al momento de crear una venta. las facturas vienen llevando la funcion que cumplia ODC en el excel
[33m51ef737[m Hice cambios para adaptar el codigo a docker, actualmente todo funciona bien, ya me puedo conectar a la pagina en la red local. ahora quiero crear el sistema de credito
[33mf105edf[m arreglados botones de eliminar ventas y eliminar productos. eliminar productos ahora es mas solido porque se eliminan en base al nro de venta y el id autoincremental, ya no utiliza el nombre del producto como argumento, por lo que no hay ningun caracter especial que pueda danar la formula
[33m5d96475[m ya arregle el boton de eliminar una venta
[33m1291e77[m ya se reflejan las ventas con el inventario. me di cuenta que se dañó la funcion de eliminar una venta, eso lo tengo que arreglar
[33mc6c40dc[m voy a crear la funcionalidad para que se reflejen las ventas en el stock
[33m514623c[m Remove .pyc files and update .gitignore
[33m5328993[m preparando el archivo para la fusion
[33m384dd41[m ya voy a hacer la fusion con la rama principal.
[33mbec9b1d[m ya funciona el prototipo de creacion de notas de entrega, ya introduce los datos en la plantilla
[33m57db268[m ya logre hacer que se introduzcan los datos en el libro prueba.xlsx, por ahora tiene el error de que introduce todos los datos de todas las ventas, pero ya por lo menos funciona, hay que seguir ajustandolo
[33m9162d67[m Estoy trancado en este punto, no entiendo por que el codigo no funciona en /generar_nota_entrega, hare pruebas a ver y si no vuelvo a este punto
[33m731190d[m Cambie el css de varias paginas, no he implementado la conexion a la base de datos cuando hay una venta
[33m6808c11[m Parece funcionar la simplificacion de registro_venta. Voy a implementar que las ventas se reflejen en la base de datos
[33m156dcf2[m Hasta este punto todo esta bien, voy a tratar de simplificar registro_venta.js
[33m4f4579f[m modularizacion de app.py: reorganizacion del codigo en diferentes archivos. implementacion de Blueprints
[33m15e7071[m Interfaz web 1.0
