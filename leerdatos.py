"""
leerdatos.py

Script sencillo para cargar y analizar el archivo `datos_sinteticos.csv`.

Funciones:
- Cargar CSV con pandas
- Mostrar las 5 primeras filas
- Resumen: forma, tipos, valores nulos, estadísticas descriptivas
- Conteos para variables categóricas
- Detección de duplicados
- Gráficas (guardadas en ./output): histogramas, boxplots y mapa de correlación

Si faltan dependencias imprime instrucciones para instalarlas.
"""

from pathlib import Path
import sys
import traceback


def main():
	try:
		import pandas as pd
		import matplotlib.pyplot as plt
		import seaborn as sns
	except Exception as e:
		print("Faltan dependencias necesarias para ejecutar el análisis.")
		print("Instala las librerías con:\n    pip install pandas matplotlib seaborn")
		print("Error de importación:", e)
		return

	sns.set(style="whitegrid")
"""
leerdatos.py

Script sencillo para cargar y analizar el archivo `datos_sinteticos.csv`.

Genera:
- Primeras 5 filas y resumen textual
- Estadísticas y valores nulos
- Histogramas y boxplots para numéricas
- Matriz de correlación
- Gráficas circulares (pie) y barras para categóricas
- Pairplot condicional y gráfico de series si hay columna fecha

Archivos de salida en la carpeta `output` (creada si no existe).
"""

from pathlib import Path
import sys
import traceback
import warnings


def safe_name(name: str) -> str:
	"""Genera un nombre de archivo seguro a partir de un nombre de columna."""
	return str(name).strip().replace(' ', '_').replace('/', '_')


def try_parse_dates(df, pd):
	# Buscar columnas que parezcan fechas
	candidates = [c for c in df.columns if any(k in c.lower() for k in ('date', 'fecha', 'time'))]
	for c in candidates:
		try:
			df[c] = pd.to_datetime(df[c], errors='coerce')
		except Exception:
			pass
	return df


def main():
	try:
		import pandas as pd
		import matplotlib.pyplot as plt
		import seaborn as sns
	except Exception as e:
		print("Faltan dependencias necesarias para ejecutar el análisis.")
		print("Instala las librerías con:\n    pip install pandas matplotlib seaborn")
		print("Error de importación:", e)
		return

	warnings.filterwarnings('ignore')
	sns.set(style="whitegrid")

	base = Path(__file__).resolve().parent
	csv_path = base / "datos_sinteticos.csv"

	if not csv_path.exists():
		print(f"No se encontró el archivo: {csv_path}")
		return

	print(f"Cargando: {csv_path}\n")
	# Intentar inferir separador y codificación de forma simple
	try:
		df = pd.read_csv(csv_path)
	except Exception:
		# Intentar con sep=';' por si es CSV separado por punto y coma
		try:
			df = pd.read_csv(csv_path, sep=';')
		except Exception:
			print("Error leyendo el CSV. Mostrar traceback:")
			traceback.print_exc()
			return

	out_dir = base / "output"
	out_dir.mkdir(exist_ok=True)

	# Primeras filas y resumen
	print("Primeras 5 filas:")
	print(df.head(5).to_string(index=False))
	print("\n---\n")

	print("Dimensiones (filas, columnas):", df.shape)
	print("\nTipos de columnas:")
	print(df.dtypes)
	print("\n---\n")

	print("Valores nulos por columna:")
	print(df.isnull().sum())
	print("\n---\n")

	print("Estadísticas descriptivas (numéricas):")
	print(df.describe(include='number').transpose())
	print("\n---\n")

	print("Estadísticas (no numéricas):")
	print(df.describe(include=['object', 'category']))
	print("\n---\n")

	dup_count = df.duplicated().sum()
	print(f"Filas duplicadas: {dup_count}")
	if dup_count > 0:
		print(df[df.duplicated()].head().to_string(index=False))

	# Detectar categóricas y numéricas
	cat_cols = [c for c in df.columns if df[c].dtype == 'object' or str(df[c].dtype).startswith('category')]
	num_cols = df.select_dtypes(include='number').columns.tolist()

	if cat_cols:
		print("\nGenerando gráficos para columnas categóricas (pie + barras)")
		for c in cat_cols:
			counts = df[c].value_counts(dropna=False)
			# Sólo graficar pies para pocas categorías (<=10)
			try:
				if counts.shape[0] <= 10:
					plt.figure(figsize=(6, 6))
					counts.plot.pie(autopct='%1.1f%%', startangle=90)
					plt.ylabel('')
					plt.title(f'Pie: {c}')
					plt.tight_layout()
					plt.savefig(out_dir / f'pie_{safe_name(c)}.png')
					plt.close()

				# Barras (top 10)
				plt.figure(figsize=(8, 4))
				counts.head(10).plot.bar()
				plt.title(f'Bar: {c} (top 10)')
				plt.ylabel('count')
				plt.tight_layout()
				plt.savefig(out_dir / f'bar_{safe_name(c)}.png')
				plt.close()
			except Exception:
				print(f"No se pudo generar gráfico para la columna categórica: {c}")

	# Gráficas numéricas (histogramas y boxplot ya existentes)
	if num_cols:
		print("\nGenerando histogramas y boxplots para columnas numéricas (guardados en ./output)")
		for c in num_cols:
			try:
				plt.figure(figsize=(8, 4))
				sns.histplot(df[c].dropna(), kde=True)
				plt.title(f"Histograma: {c}")
				plt.tight_layout()
				plt.savefig(out_dir / f"hist_{safe_name(c)}.png")
				plt.close()

				plt.figure(figsize=(6, 4))
				sns.boxplot(x=df[c].dropna())
				plt.title(f"Boxplot: {c}")
				plt.tight_layout()
				plt.savefig(out_dir / f"box_{safe_name(c)}.png")
				plt.close()
			except Exception:
				print(f"No se pudo graficar la columna numérica: {c}")

		# Correlación
		if len(num_cols) > 1:
			try:
				print("Generando mapa de correlación (guardado en ./output/correlation_matrix.png)")
				corr = df[num_cols].corr()
				plt.figure(figsize=(max(6, len(num_cols)), max(4, len(num_cols) / 2)))
				sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', square=True)
				plt.title('Matriz de correlación')
				plt.tight_layout()
				plt.savefig(out_dir / 'correlation_matrix.png')
				plt.close()
			except Exception:
				print("No se pudo generar la matriz de correlación")

		# Pairplot condicional (si no hay demasiadas columnas numéricas)
		if 2 <= len(num_cols) <= 6:
			try:
				print("Generando pairplot (guardado en ./output/pairplot.png)")
				pp = sns.pairplot(df[num_cols].dropna())
				pp.savefig(out_dir / 'pairplot.png')
				plt.close()
			except Exception:
				print("No se pudo generar pairplot")

	else:
		print("No se detectaron columnas numéricas para graficar.")

	# Intentar detectar columnas de fecha y generar una serie simple
	try:
		df = try_parse_dates(df, pd)
		date_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
		if date_cols:
			# Usar la primera columna fecha
			dcol = date_cols[0]
			print(f"Generando gráfico de serie temporal por fecha usando: {dcol}")
			tmp = df.set_index(dcol).resample('D').size()
			plt.figure(figsize=(10, 4))
			tmp.plot()
			plt.title(f'Conteo por día ({dcol})')
			plt.ylabel('count')
			plt.tight_layout()
			plt.savefig(out_dir / f'timeseries_{safe_name(dcol)}.png')
			plt.close()
	except Exception:
		pass

	print(f"\nAnálisis completado. Archivos de salida en: {out_dir}")


if __name__ == '__main__':
	main()


