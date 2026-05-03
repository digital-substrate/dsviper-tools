from __future__ import annotations

from PySide6.QtCore import Signal, Qt, QRectF, QPointF
from PySide6.QtGui import (
    QPaintEvent, QMouseEvent, QKeyEvent, QColor, QGuiApplication, QPainter, QPen, QPainterPath,
    QFont, QFontMetricsF, QTextOption)
from PySide6.QtWidgets import QWidget, QScrollArea
from dsviper import CommitStore, ValueCommitId, CommitNode, CommitNodeGrid, CommitNodeGridBuilder, ViperError

BACKGROUND_COLOR = QColor(30, 30, 30)
SYSTEM_BLUE_COLOR = QColor(59, 129, 247)
SYSTEM_GREEN_COLOR = QColor(107, 212, 96)
SYSTEM_RED_COLOR = QColor(236, 85, 69)
SYSTEM_ORANGE_COLOR = QColor(242, 165, 95)
SYSTEM_YELLOW_COLOR = QColor(248, 216, 74)
SYSTEM_BROWN_COLOR = QColor(167, 144, 209)
SYSTEM_PURPLE_COLOR = QColor(179, 96, 234)
SYSTEM_CYAN_COLOR = QColor(120, 197, 241)
SYSTEM_INDIGO_COLOR = QColor(94, 92, 222)
SYSTEM_MINT_COLOR = QColor(135, 227, 225)

NODE_COLORS = {
    "Enable": SYSTEM_GREEN_COLOR,
    "Disable": SYSTEM_RED_COLOR,
    "Merge": SYSTEM_PURPLE_COLOR,
    "Mutations": SYSTEM_BLUE_COLOR
}

MARGIN = 4
NODE_SIZE = 17
NODE_SPACING_X = NODE_SIZE + 4
NODE_SPACING_Y = NODE_SIZE + 2


class DSCommitsView(QWidget):
    selection_changed = Signal(ValueCommitId)
    mark_selection_changed = Signal(ValueCommitId)

    def __init__(self, store: CommitStore, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.store = store
        self._marked_commit_id: ValueCommitId | None = None
        self._grid_root: CommitNodeGrid | None = None
        self._nodes: dict[ValueCommitId, CommitNodeGrid] = dict()
        self._enabled_by_commit_id: dict[ValueCommitId, bool] = dict()
        self._order_by_commit_id: dict[ValueCommitId, int] = dict()

    @property
    def marked_commit_id(self) -> ValueCommitId | None:
        return self._marked_commit_id

    @marked_commit_id.setter
    def marked_commit_id(self, value: ValueCommitId):
        self._marked_commit_id = value

    # Update
    def update_store(self):
        try:
            self._build()
            self.update()

        except ViperError as e:
            self._except_present(e)

    def update_commit_states(self, commit_id: ValueCommitId):
        try:
            state = self.store.state()
            self._enabled_by_commit_id = self.store.database().enabled_by_commit_id(commit_id)
            self._order_by_commit_id.clear()
            # eval_actions() returns reverse chronological order, reverse for evaluation order
            eval_actions = reversed(state.eval_actions())
            order = 1
            for eval_action in eval_actions:
                self._order_by_commit_id[eval_action.header().commit_id()] = order
                order += 1
        except ViperError as e:
            self._except_present(e)

    def update_graph(self, follow_current_commit_id: bool, area: QScrollArea):
        try:
            if not self.store.has_database():
                return

            current_commit_id = self.store.state().commit_id()

            if not current_commit_id in self._nodes:
                self._build()
                self.update()

            if follow_current_commit_id:
                node = self._nodes[current_commit_id]
                rect = self._node_rect(node)
                area.ensureVisible(int(rect.center().x()), int(rect.center().y()))
            else:
                self.update()

        except ViperError as e:
            self._except_present(e)

    def mousePressEvent(self, event: QMouseEvent):
        if not self._grid_root:
            return

        self.setFocus()
        modifiers = QGuiApplication.keyboardModifiers()
        is_option_pressed = modifiers.value & Qt.KeyboardModifier.AltModifier.value == Qt.KeyboardModifier.AltModifier.value
        location = event.localPos()

        if node := self._pick_node(location):
            if is_option_pressed:
                self.mark_selection_changed.emit(node.header().commit_id())
            else:
                self.selection_changed.emit(node.header().commit_id())

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Up:
            self._move_up()
        elif event.key() == Qt.Key.Key_Down:
            self._move_down()
        elif event.key() == Qt.Key.Key_Left:
            self._move_left()
        elif event.key() == Qt.Key.Key_Right:
            self._move_right()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), BACKGROUND_COLOR)
        if self._grid_root is None:
            return

        visited = self._collect_nodes()
        self._draw_edges(painter, visited)
        self._draw_merges(painter, visited)
        self._draw_nodes(painter, visited)
        self._draw_orders(painter, visited)

    def _collect_nodes(self) -> list[CommitNodeGrid]:
        result: list[CommitNodeGrid] = []
        current = 0
        result.extend(self._grid_root.children())

        while current < len(result):
            result.extend(result[current].children())
            current += 1

        return result

    def _move_up(self):
        try:
            commit_id = self.store.state().commit_id()
            if node := self._nodes.get(commit_id):
                if node.has_children():
                    self.selection_changed.emit(node.children()[0].header().commit_id())

        except ViperError as e:
            self._except_present(e)

    def _move_down(self):
        try:
            commit_id = self.store.state().commit_id()
            if node := self._nodes.get(commit_id):
                if node.parent and node.parent().header().commit_id().is_valid():
                    self.selection_changed.emit(node.parent().header().commit_id())

        except ViperError as e:
            self._except_present(e)

    def _move_left(self):
        self._sibling(-1)

    def _move_right(self):
        self._sibling(+1)

    def _sibling(self, direction: int):
        try:
            commit_id = self.store.state().commit_id()
            node = self._nodes.get(commit_id)
            if node is None:
                return

            if node.header().commit_type() == "Merge":
                self.selection_changed.emit(node.header().target_commit_id())
                return

            parent = node.parent()
            if not (parent and parent.header().commit_id().is_valid() and parent.child_count() > 1):
                return

            index = 0
            children = parent.children()
            for child in children:
                if child.header().commit_id() == node.header().commit_id():
                    break
                index += 1

            if index != parent.child_count():
                next_child_index = (index + parent.child_count() + direction) % parent.child_count()
                self.selection_changed.emit(children[next_child_index].header().commit_id())

        except ViperError as e:
            self._except_present(e)

    # Build
    def _build(self):
        self._grid_root = None
        self._nodes.clear()

        if not self.store.has_database():
            return

        database = self.store.database()
        root = CommitNode.build(database)
        builder = CommitNodeGridBuilder.build(root)
        self._grid_root = builder.root()
        self._nodes = builder.nodes()
        width = builder.column_max() * NODE_SPACING_X + NODE_SIZE + MARGIN * 2
        height = builder.row_max() * NODE_SPACING_Y + MARGIN * 2

        self.setMinimumSize(width, height)

    # Draw order
    def _draw_orders(self, painter: QPainter, nodes: list[CommitNodeGrid]):
        for node in nodes:
            self._draw_order(painter, node)

    def _draw_order(self, painter: QPainter, node: CommitNodeGrid):
        node_commit_id = node.header().commit_id()
        if node_commit_id == self.store.state().commit_id():
            return

        if order := self._order_by_commit_id.get(node_commit_id):
            node_rect = self._node_rect(node)
            text = str(order)
            font = QFont()
            font.setPointSize(8)
            fm = QFontMetricsF(font)
            text_rect = fm.boundingRect(text, QTextOption(Qt.AlignmentFlag.AlignCenter))
            painter.setFont(font)
            painter.setPen(SYSTEM_YELLOW_COLOR)
            painter.drawText(node_rect.center() - text_rect.center(), text)

    # Draw Merge
    def _draw_merges(self, painter: QPainter, nodes: list[CommitNodeGrid]):
        for node in nodes:
            if node.header().commit_type() == "Merge":
                if target_node := self._nodes.get(node.header().target_commit_id()):
                    self._draw_merge(painter, node, target_node)

    def _draw_merge(self, painter: QPainter, node: CommitNodeGrid, target_node: CommitNodeGrid):
        node_rect = self._node_rect(node)
        target_rect = self._node_rect(target_node)

        color = self._node_color(node)
        if target_node.header().commit_id() not in self._enabled_by_commit_id:
            color = Qt.GlobalColor.gray

        if node_rect.center().x() > target_rect.center().x():
            c1 = QPointF(target_rect.right() + 2, node_rect.center().y())
            c2 = QPointF(target_rect.right() + 2, target_rect.center().y())
        else:
            c1 = QPointF(target_rect.left() - 2, node_rect.center().y())
            c2 = QPointF(target_rect.left() - 2, target_rect.center().y())

        pen = QPen()
        pen.setColor(color)
        pen.setWidthF(1)

        path = QPainterPath()
        path.moveTo(node_rect.center())
        path.lineTo(c1)
        path.lineTo(c2)
        path.lineTo(target_rect.center())

        painter.setPen(pen)
        painter.drawPath(path)

    # Draw Edge
    def _draw_edges(self, painter: QPainter, nodes: list[CommitNodeGrid]):
        for node in nodes:
            if node.commit_id().is_valid() and node.parent().commit_id().is_valid():
                self._draw_edge(painter, node)

    def _draw_edge(self, painter: QPainter, node: CommitNodeGrid):
        parent_rect = self._node_rect(node.parent())
        child_rect = self._node_rect(node)

        parent_color = self._node_color(node.parent())
        child_color = self._node_color(node)

        parent_center = parent_rect.center()
        child_center = child_rect.center()

        p = QPen()
        p.setColor(parent_color)
        p.setWidthF(1.5)
        painter.setPen(p)

        path = QPainterPath()
        path.moveTo(parent_center.x(), parent_center.y())
        path.lineTo(child_center.x(), parent_center.y())
        painter.drawPath(path)

        p.setColor(child_color)
        painter.setPen(p)

        path = QPainterPath()
        path.moveTo(child_center.x(), parent_center.y())
        path.lineTo(child_center.x(), child_center.y())
        painter.drawPath(path)

        dot_size = 5.0
        half_dot_size = dot_size / 2.0
        connection_rect = QRectF(child_center.x() - half_dot_size, parent_center.y() - half_dot_size, dot_size,
                                 dot_size)

        p.setColor(parent_color)
        painter.setPen(p)

        path = QPainterPath()
        path.addEllipse(connection_rect)
        painter.fillPath(path, parent_color)

    # Draw Node
    def _draw_nodes(self, painter: QPainter, nodes: list[CommitNodeGrid]):
        for node in nodes:
            self._draw_node(painter, node)

    def _draw_node(self, painter: QPainter, node: CommitNodeGrid):
        if not node.commit_id().is_valid():
            return

        outer_rect = self._node_rect(node)
        inner_rect = outer_rect.adjusted(1, 1, -1, -1)

        color = self._node_color(node)
        path = self._node_path(inner_rect)

        painter.fillPath(path, BACKGROUND_COLOR)

        pen = QPen()
        pen.setWidthF(1.5)
        pen.setColor(color)
        painter.setPen(pen)
        painter.drawPath(path)

        if self.store.has_database():
            current_commit = self.store.state().commit_id()
            if node.header().commit_id() == current_commit:
                rect = inner_rect.adjusted(3, 3, -3, -3)
                p = QPainterPath()
                p.addEllipse(rect)
                painter.fillPath(p, color)

        if self.marked_commit_id and node.header().commit_id() == self.marked_commit_id:
            square_rect = outer_rect.adjusted(-1.5, -1.5, 1.5, 1.5)
            p = QPainterPath()
            p.addEllipse(square_rect)
            pen.setColor(QColor(255, 255, 255))
            pen.setDashPattern([4, 2])
            pen.setWidthF(1.5)
            painter.setPen(pen)
            painter.drawPath(p)

    def _node_path(self, rect: QRectF) -> QPainterPath:
        p = QPainterPath()
        p.addEllipse(rect)
        return p

    def _node_rect(self, node: CommitNodeGrid) -> QRectF:
        x = MARGIN + node.column() * NODE_SPACING_X
        y = self.height() - MARGIN - node.row() * NODE_SPACING_Y
        return QRectF(x, y, NODE_SIZE, NODE_SIZE)

    def _node_color(self, node: CommitNodeGrid):
        header = node.header()
        commit_id = header.commit_id()
        if commit_id in self._enabled_by_commit_id:
            if self._enabled_by_commit_id[commit_id]:
                return NODE_COLORS[header.commit_type()]

        return QColor(Qt.GlobalColor.gray)

    def _node(self, commit_id: ValueCommitId) -> CommitNodeGrid | None:
        return self._nodes.get(commit_id)

    # Picking
    def _pick_node(self, location: QPointF) -> CommitNodeGrid | None:
        for _, node in self._nodes.items():
            rect = self._node_rect(node)
            if rect.contains(location):
                return node
        return None

    def _except_present(self, e: ViperError):
        print(e)
