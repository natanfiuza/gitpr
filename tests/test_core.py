import unittest
from unittest.mock import patch, MagicMock
from src.core import get_current_branch, get_git_diff

class TestCore(unittest.TestCase):

    @patch('src.core.subprocess.run')
    def test_get_current_branch_success(self, mock_subprocess):
        """Testa se a função retorna corretamente o nome da branch simulada."""
        # Configura o mock para "fingir" o retorno do terminal
        mock_process = MagicMock()
        mock_process.stdout = "feature/nova-tela\n"
        mock_subprocess.return_value = mock_process
        
        branch = get_current_branch()
        self.assertEqual(branch, "feature/nova-tela")

    @patch('src.core.subprocess.run')
    def test_get_git_diff_success(self, mock_subprocess):
        """Testa se o diff é capturado corretamente."""
        mock_process = MagicMock()
        mock_process.stdout = "+ print('Hello World da IA')"
        mock_subprocess.return_value = mock_process
        
        diff = get_git_diff()
        self.assertEqual(diff, "+ print('Hello World da IA')")

if __name__ == '__main__':
    unittest.main()