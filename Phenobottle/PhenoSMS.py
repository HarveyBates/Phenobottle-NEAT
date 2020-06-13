class Readings:
    def send_message():
        global message_sent
        if not message_sent:
            try:
                client = Client(account_ssid_var, account_token_var)
                client.messages.create(body='Phenobottle No.%s is approching saturation. Please change the reference voltage.' %PHENOBOTTLE_NUMBER,
                                            from_=from_number,
                                            to=to_number)
                print("Message sent")
                message_sent = True
            except:
                print("Fm at saturation, but there was an error...")
        else:
            pass

    @staticmethod
    def test_saturation():
        if fm >= (ARDUINO_FLUORESCENCE_REFERENCE * 0.9):
            Readings.send_message()
        else:
            pass