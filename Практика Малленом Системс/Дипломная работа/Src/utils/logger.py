import csv

class TrafficLogger:
    @staticmethod
    def save_data(file_path, headers, data):
        try:
            if file_path.endswith('.csv'):
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(data)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("\t".join(headers) + "\n")
                    for row in data:
                        f.write("\t".join(map(str, row)) + "\n")
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False