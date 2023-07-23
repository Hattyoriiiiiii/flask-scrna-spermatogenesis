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
        img = io.BytesIO()
        for i in range(len(filtered_data)):
            plt.plot(filtered_data.columns[1:], filtered_data.iloc[i, 1:])
        plt.title('Gene Expression during spermatogenesis')
        if normalize:
            plt.ylabel('Expression (z-score)')
        else:
            plt.ylabel('Expression (TP10K)')
        if len(filtered_data) <= 10:
            # plt.legend(filtered_data['symbol'], loc='upper left')
            plt.legend(filtered_data['symbol'], loc='best')
        plt.xticks(rotation=30)
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