def gerar_retorno_situacao(situacao):
        
        if situacao == "parametro para validar"():
            json_reportar_correto = {"clientKey": API_KEY["KEY"], "taskId": task_id}
            gerar_request_correto = requests.post(TWO_CAPCHA_METHOD["REPORT_CORRECT"], json=json_reportar_correto)

            if gerar_request_correto.get("errorId") != 0:
                raise Exception(f"[ERRO] Falha ao criar task: {create_result}")
            
            return print("[WARN] Retorno Gerado para API: CORRETO")
        
        else:
            json_reportar_incorreto = {"clientKey": API_KEY["KEY"], "taskId": task_id}
            gerar_request_incorreto = requests.post(TWO_CAPCHA_METHOD["REPORT_INCORRECT"], json=json_reportar_incorreto)

            if gerar_request_incorreto.get("errorId") != 0:
                raise Exception(f"[ERRO] Falha ao criar task: {create_result}")
            
            return print("[WARN] Retorno Gerado para API: INCORRETO")