from flask import Flask, render_template, request, jsonify
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from datetime import datetime
import json

app = Flask(__name__)
load_dotenv()

class ProjeAsistani:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    def proje_olustur(self, konu, proje_turu, butce, sure):
        prompt = f"""
        Lütfen aşağıdaki proje için detaylı bir öneri hazırla:

        PROJE BİLGİLERİ:
        Konu: {konu}
        Tür: {proje_turu}
        Bütçe: {butce}
        Süre: {sure}

        Lütfen önerinizi şu başlıklar altında detaylandırın:

        # PROJE ÖZETİ
        [Projenin amacını ve gerekçesini açıklayın]

        # HEDEFLER
        * Ana Hedef:
        * Alt Hedefler:

        # FAALİYETLER
        1. AY 1-2:
        * [Faaliyetler]

        2. AY 3-4:
        * [Faaliyetler]

        3. AY 5-6:
        * [Faaliyetler]

        # BÜTÇE DAĞILIMI
        * Personel Giderleri:
        * Ekipman ve Malzeme:
        * Eğitim ve Organizasyon:
        * Diğer Giderler:

        # BEKLENEN ÇIKTILAR
        * [Çıktılar listesi]

        # RİSK ANALİZİ
        * Olası Riskler:
        * Risk Yönetimi:
        """

        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                messages=[{
                    "role": "user", 
                    "content": prompt
                }],
                max_tokens=4000
            )
            return str(response.content)
        except Exception as e:
            return f"Bir hata oluştu: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/olustur', methods=['POST'])
def olustur():
    data = request.json
    asistan = ProjeAsistani()
    proje = asistan.proje_olustur(
        data['konu'],
        data['tur'],
        data['butce'],
        data['sure']
    )
    
    # Dosya adı oluştur
    tarih = datetime.now().strftime("%Y%m%d_%H%M%S")
    dosya_adi = f"proje_{tarih}.txt"
    
    try:
        # Projeyi kaydet
        os.makedirs('projeler', exist_ok=True)
        with open(f'projeler/{dosya_adi}', 'w', encoding='utf-8') as f:
            json.dump({
                'konu': data['konu'],
                'tur': data['tur'],
                'butce': data['butce'],
                'sure': data['sure'],
                'icerik': proje
            }, f, ensure_ascii=False, indent=4)
        
        return jsonify({
            'success': True,
            'proje': proje,
            'dosya': dosya_adi
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    os.makedirs('projeler', exist_ok=True)
    app.run(debug=True)
