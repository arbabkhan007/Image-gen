import pytest
import torch
from unittest.mock import patch, MagicMock

mock_nodes = MagicMock()
mock_nodes.MAX_RESOLUTION = 16384
mock_server = MagicMock()

with patch.dict("sys.modules", {"nodes": mock_nodes, "server": mock_server}):
    from comfy_extras.nodes_mask import MaskComposite


class TestMaskCompositeOperations:
    @staticmethod
    def _exec(destination, source, operation):
        d = torch.tensor([[destination]])
        s = torch.tensor([[source]])
        return MaskComposite.execute(d, s, 0, 0, operation).result[0].flatten().tolist()

    def test_max_is_union_of_soft_masks(self):
        result = self._exec([0.0, 0.25, 0.75, 1.0], [0.5, 0.5, 0.5, 0.5], "max")
        assert result == pytest.approx([0.5, 0.5, 0.75, 1.0])

    def test_min_is_intersection_of_soft_masks(self):
        result = self._exec([0.0, 0.25, 0.75, 1.0], [0.5, 0.5, 0.5, 0.5], "min")
        assert result == pytest.approx([0.0, 0.25, 0.5, 0.5])

    def test_max_preserves_intermediate_values(self):
        # Unlike "or", max must not round feathered values to 0 or 1.
        result = self._exec([0.25, 0.75], [0.0, 0.0], "max")
        assert result == pytest.approx([0.25, 0.75])

    def test_min_preserves_intermediate_values(self):
        result = self._exec([0.25, 0.75], [1.0, 1.0], "min")
        assert result == pytest.approx([0.25, 0.75])

    def test_or_binarizes(self):
        # Documents existing behaviour that motivates max/min.
        result = self._exec([0.25, 0.75], [0.0, 0.0], "or")
        assert result == pytest.approx([0.0, 1.0])

    def test_max_is_commutative(self):
        a = self._exec([0.3, 0.8], [0.6, 0.1], "max")
        b = self._exec([0.6, 0.1], [0.3, 0.8], "max")
        assert a == pytest.approx(b)

    def test_min_is_commutative(self):
        a = self._exec([0.3, 0.8], [0.6, 0.1], "min")
        b = self._exec([0.6, 0.1], [0.3, 0.8], "min")
        assert a == pytest.approx(b)

    def test_max_with_empty_mask_is_identity(self):
        result = self._exec([0.0, 0.4, 1.0], [0.0, 0.0, 0.0], "max")
        assert result == pytest.approx([0.0, 0.4, 1.0])

    def test_min_with_full_mask_is_identity(self):
        result = self._exec([0.0, 0.4, 1.0], [1.0, 1.0, 1.0], "min")
        assert result == pytest.approx([0.0, 0.4, 1.0])
