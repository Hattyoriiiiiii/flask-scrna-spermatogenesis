from flask import Flask, render_template, request, send_file
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import urllib

app = Flask(__name__)

# データフレームの初期化
data = pd.read_csv('sceRNA.csv')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['gene_file']
        if file and file.filename != '':
            input_genes = file.read().decode().splitlines()
        else:
            input_genes = request.form['gene_names'].replace(" ","").split(',')
        
        normalize = request.form.get('zscore') == 'on'
        filtered_data = data[data['symbol'].isin(input_genes)]
        if normalize:
            filtered_data.iloc[:, 1:] = filtered_data.iloc[:, 1:].apply(lambda x: (x - x.mean()) / x.std(), axis=1)
        
        # Create the subplot layout
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(15, 5))
        
        for i in range(len(filtered_data)):
            axes[0].plot(filtered_data.columns[1:], filtered_data.iloc[i, 1:])
        axes[0].set_title('Gene Expression during spermatogenesis')
        if normalize:
            axes[0].set_ylabel('Expression (z-score)')
        else:
            axes[0].set_ylabel('Expression (TP10K)')
        if len(filtered_data) <= 10:
            # axes[0].legend(filtered_data['symbol'], loc='upper left')
            axes[0].legend(filtered_data['symbol'], loc='best')
        axes[0].set_xticklabels(filtered_data.columns[1:], rotation=30)
        
        # average, median, and quantiles across all genes
        numeric_columns = filtered_data.columns[1:]
        average_expression = filtered_data[numeric_columns].mean()
        median_expression = filtered_data[numeric_columns].median()
        first_quantile = filtered_data[numeric_columns].quantile(0.25)
        third_quantile = filtered_data[numeric_columns].quantile(0.75)

        # plot the average expression
        axes[1].plot(filtered_data.columns[1:], average_expression, label="Average")

        # plot the median expression
        axes[1].plot(filtered_data.columns[1:], median_expression, label="Median")

        # plot quantiles
        axes[1].plot(filtered_data.columns[1:], first_quantile, label="First quantile", linestyle='dashed')
        axes[1].plot(filtered_data.columns[1:], third_quantile, label="Third quantile", linestyle='dashed')

        axes[1].set_title('Summary Statistics of Gene Expression during spermatogenesis')
        axes[1].set_ylabel('Expression')
        axes[1].set_xticklabels(filtered_data.columns[1:], rotation=30)
        axes[1].legend()
        
        img = io.BytesIO()
        plt.tight_layout()
        plt.savefig(img, format='png')
        plt.close()
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        return '<img src="data:image/png;base64,{}">'.format(plot_url)
    return render_template('index.html')

@app.route('/download')
def download_file():
    return send_file('input.txt', as_attachment=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000", debug=True)
