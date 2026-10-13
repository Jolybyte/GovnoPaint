import numpy as np
from PyQt6.QtGui import QImage
from collections import deque

class FloodFill:
    @staticmethod
    def flood_fill_numpy(image, point, color):
        """Высокооптимизированная заливка с использованием numpy и векторизации."""
        # Быстрая проверка входных данных
        if image is None or image.width() == 0 or image.height() == 0:
            return image
        
        # Преобразование в ARGB32 если нужно (одна операция)
        if image.format() != QImage.Format.Format_ARGB32:
            image = image.convertToFormat(QImage.Format.Format_ARGB32)
        
        width = image.width()
        height = image.height()
        
        # Проверка границ точки
        x0, y0 = point.x(), point.y()
        if not (0 <= x0 < width and 0 <= y0 < height):
            return image
        
        # Получаем указатель на данные
        ptr = image.bits()
        if ptr is None:
            return image
        
        # Размер данных
        byte_count = width * height * 4
        ptr.setsize(byte_count)
        
        # Конвертируем в numpy массив как одномерный буфер
        # Используем memoryview для более быстрого доступа
        img_buffer = np.frombuffer(memoryview(ptr), dtype=np.uint8, count=byte_count)
        
        # Переформатируем в массив с высотой и шириной
        # Используем reshape без копирования если возможно
        img_array = img_buffer.reshape(height, width, 4)
        
        # Целевой цвет и цвет заливки как 32-битные значения для быстрого сравнения
        target_rgba = img_array[y0, x0].view(np.uint32)[0]
        fill_rgba = np.array([color.blue(), color.green(), color.red(), color.alpha()], 
                            dtype=np.uint8).view(np.uint32)[0]  # BGRA порядок
        
        # Если цвета совпадают - сразу возвращаем
        if target_rgba == fill_rgba:
            return image
        
        # Преобразуем массив к 32-битному представлению для быстрого сравнения
        img_flat = img_buffer.view(np.uint32).reshape(height, width)
        
        # Создаем маску посещенных пикселей как булев массив
        visited = np.zeros((height, width), dtype=bool)
        
        # Стек вместо очереди - быстрее для большинства случаев заливки
        stack = [(x0, y0)]
        visited[y0, x0] = True
        
        # Ограничиваем максимальное количество итераций для безопасности
        max_iterations = width * height
        iterations = 0
        
        # Предварительно вычисленные сдвиги
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # право, лево, низ, верх
        
        # Быстрый inline-цикл
        while stack:
            x, y = stack.pop()
            
            # Заливаем текущий пиксель
            img_flat[y, x] = fill_rgba
            
            # Проверяем соседей
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                # Быстрая проверка границ
                if 0 <= nx < width and 0 <= ny < height:
                    if not visited[ny, nx] and img_flat[ny, nx] == target_rgba:
                        visited[ny, nx] = True
                        stack.append((nx, ny))
            
            iterations += 1
            if iterations > max_iterations:
                break  # Защита от бесконечного цикла
        
        # Оптимизация для больших изображений - альтернативный алгоритм scanline
        if width * height > 1000000:  # Для очень больших изображений
            return FloodFill._scanline_fill(image, point, color)
        
        # Создаем новое изображение напрямую из буфера
        result_image = QImage(img_buffer.data, width, height, QImage.Format.Format_ARGB32)
        # Делаем копию, чтобы буфер не очищался
        return result_image.copy()
    
    @staticmethod
    def _scanline_fill(image, point, color):
        """Scanline алгоритм заливки для очень больших изображений."""
        if image.format() != QImage.Format.Format_ARGB32:
            image = image.convertToFormat(QImage.Format.Format_ARGB32)
        
        width = image.width()
        height = image.height()
        
        ptr = image.bits()
        byte_count = width * height * 4
        ptr.setsize(byte_count)
        
        img_buffer = np.frombuffer(memoryview(ptr), dtype=np.uint8, count=byte_count)
        img_array = img_buffer.reshape(height, width, 4)
        
        x0, y0 = point.x(), point.y()
        target_color = img_array[y0, x0].copy()
        fill_color = np.array([color.blue(), color.green(), color.red(), color.alpha()], 
                             dtype=np.uint8)
        
        if np.array_equal(target_color, fill_color):
            return image
        
        # Scanline flood fill
        stack = [(x0, y0)]
        img_flat = img_buffer.view(np.uint32).reshape(height, width)
        target_rgba = img_array[y0, x0].view(np.uint32)[0]
        fill_rgba = fill_color.view(np.uint32)[0]
        
        while stack:
            x, y = stack.pop()
            
            # Находим левую границу
            l = x
            while l >= 0 and img_flat[y, l] == target_rgba:
                l -= 1
            l += 1
            
            # Находим правую границу
            r = x
            while r < width and img_flat[y, r] == target_rgba:
                r += 1
            
            # Заливаем строку
            img_flat[y, l:r] = fill_rgba
            
            # Проверяем строки выше и ниже
            for ny in (y - 1, y + 1):
                if 0 <= ny < height:
                    # Ищем сегменты для заливки
                    nx = l
                    while nx < r:
                        if img_flat[ny, nx] == target_rgba:
                            start = nx
                            while nx < r and img_flat[ny, nx] == target_rgba:
                                nx += 1
                            if nx > start:
                                stack.append((start, ny))
                        else:
                            nx += 1
        
        result_image = QImage(img_buffer.data, width, height, QImage.Format.Format_ARGB32)
        return result_image.copy()
    
    @staticmethod
    def flood_fill_parallel(image, point, color):
        """Параллельная заливка с использованием многопоточности (для очень больших изображений)."""
        try:
            from concurrent.futures import ThreadPoolExecutor
            import threading
            
            if image.format() != QImage.Format.Format_ARGB32:
                image = image.convertToFormat(QImage.Format.Format_ARGB32)
            
            width = image.width()
            height = image.height()
            
            ptr = image.bits()
            byte_count = width * height * 4
            ptr.setsize(byte_count)
            
            img_buffer = np.frombuffer(memoryview(ptr), dtype=np.uint8, count=byte_count)
            img_flat = img_buffer.view(np.uint32).reshape(height, width)
            
            x0, y0 = point.x(), point.y()
            target_rgba = img_flat[y0, x0]
            fill_rgba = np.array([color.blue(), color.green(), color.red(), color.alpha()], 
                                dtype=np.uint8).view(np.uint32)[0]
            
            if target_rgba == fill_rgba:
                return image
            
            # Разделяем изображение на полосы для параллельной обработки
            num_threads = min(4, height // 100)  # Не более 4 потоков
            if num_threads < 2:
                return FloodFill.flood_fill_numpy(image, point, color)
            
            strip_height = height // num_threads
            locks = [threading.Lock() for _ in range(width)]
            
            def fill_strip(start_y, end_y):
                # Локальная заливка для полосы
                local_visited = np.zeros((end_y - start_y, width), dtype=bool)
                stack = []
                
                # Находим начальные точки в этой полосе
                if start_y <= y0 < end_y:
                    stack.append((x0, y0 - start_y))
                    local_visited[y0 - start_y, x0] = True
                
                while stack:
                    x, y_local = stack.pop()
                    y_global = y_local + start_y
                    
                    img_flat[y_global, x] = fill_rgba
                    
                    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        nx, ny_local = x + dx, y_local + dy
                        ny_global = ny_local + start_y
                        
                        if 0 <= nx < width and 0 <= ny_local < (end_y - start_y):
                            if not local_visited[ny_local, nx] and img_flat[ny_global, nx] == target_rgba:
                                local_visited[ny_local, nx] = True
                                stack.append((nx, ny_local))
            
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = []
                for i in range(num_threads):
                    start_y = i * strip_height
                    end_y = (i + 1) * strip_height if i != num_threads - 1 else height
                    futures.append(executor.submit(fill_strip, start_y, end_y))
                
                # Ждем завершения всех потоков
                for future in futures:
                    future.result()
            
            result_image = QImage(img_buffer.data, width, height, QImage.Format.Format_ARGB32)
            return result_image.copy()
            
        except ImportError:
            # Если concurrent.futures недоступен, используем обычный метод
            return FloodFill.flood_fill_numpy(image, point, color)