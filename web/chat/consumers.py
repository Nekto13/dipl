# Импорт для работы с JSON
import json
# Импорт для асинхронного программирования
from channels.generic.websocket import AsyncWebsocketConsumer
# Импорт для работы с БД в асинхронном режиме
from channels.db import database_sync_to_async
# Импорт модели сообщений
from .models import Message


# Класс ChatConsumer
class ChatConsumer(AsyncWebsocketConsumer):

    # Метод подключения к WS
    async def connect(self):
        # Назначим пользователя в комнату
        self.room_group_name = "1"
        # Добавляем новую комнату
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # Принимаем подключаем
        await self.accept()

    # Метод для отключения пользователя
    async def disconnect(self, close_code):
        # Отключаем пользователя
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Декоратор для работы с БД в асинхронном режиме
    @database_sync_to_async
    # Функция для создания нового сообщения в БД
    def new_message(self, message):
        # Создаём сообщение в БД
        Message.objects.create(text=message)

    # Принимаем сообщение от пользователя
    async def receive(self, text_data=None, bytes_data=None):
        # Форматируем сообщение из JSON
        text_data_json = json.loads(text_data)
        # Получаем текст сообщения
        message = text_data_json['message']

        # Добавляем сообщение в БД
        await self.new_message(message=message)

        # Отправляем сообщение
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
            }
        )

    # Метод для отправки сообщения клиентам
    async def chat_message(self, event):
        # Получаем сообщение от receive
        message = event['message']
        # Отправляем сообщение клиентам
        await self.send(text_data=json.dumps({
            'message': message,
        }, ensure_ascii=False))