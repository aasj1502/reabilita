Private Sub Workbook_Open()
    MsgBox "Bem vindos a um Rascunho Incipiente do Sistema!!!"
    UF_CadetesLesões.Show
End Sub


Private Sub B_DecAtiv_Click()
    UF_CadetesLesões.CB_TFMTAF.Enabled = False
    UF_CadetesLesões.CB_Atividade.Enabled = True
End Sub

Private Sub B_Inicial_Click()
    UF_CadetesLesões.F_Retorno.Enabled = False
    UF_CadetesLesões.F_Lesão.Enabled = True
End Sub

Private Sub B_Preventiva_Click()
    UF_CadetesLesões.CB_TFMTAF.Enabled = False
    UF_CadetesLesões.CB_Atividade.Enabled = True
End Sub

Private Sub B_Retorno_Click()
    UF_CadetesLesões.F_Lesão.Enabled = True
    UF_CadetesLesões.F_Retorno.Enabled = True
    If UF_CadetesLesões.TB_NúmeroCad.Value <> "" Then
        Call RecuperaDados(UF_CadetesLesões.TB_NúmeroCad.Value, 0)
    End If
End Sub

'Private Sub B_Retorno_Click()
'    If UF_CadetesLesões.TB_NúmeroCad.Value <> "" Then
'        Call RecuperaDados(UF_CadetesLesões.TB_NúmeroCad.Value)
'    End If
'End Sub

Private Sub B_Sair_Click()
    Unload UF_CadetesLesões
End Sub

Private Sub CB_Atividade_Change()
    If CB_Atividade.Value = "TFM/TAF" Then
        CB_TFMTAF.Enabled = True
    Else
        CB_TFMTAF.Enabled = False
    End If
    If CB_Atividade.Value = "Acadêmicas" Or CB_Atividade.Value = "Treino atleta" Or CB_Atividade.Value = "NAVAMAER" Then
        CB_Modalidade.Enabled = True
    Else
        CB_Modalidade.Enabled = False
    End If
End Sub

Private Sub CB_DataRet_Click()
    Call RecuperaDados(UF_CadetesLesões.TB_NúmeroCad.Value, 1)
End Sub

Private Sub CB_HoraRet_Click()
    Call DadosRetorno
End Sub

Private Sub CB_Lesões_AfterUpdate()
    Dim linha As Integer
    Dim coluna As Integer
    
    Select Case UF_CadetesLesões.CB_Lesões.Value
        Case "Óssea"
            Call CBPreenche(2, Sheets("Geral"), 3, 6, 0)
        Case "Articular"
            Call CBPreenche(2, Sheets("Geral"), 3, 6, 0)
        Case "Muscular"
            Call CBPreenche(3, Sheets("Geral"), 3, 7, 0)
        Case "Tendinosa"
            Call CBPreenche(4, Sheets("Geral"), 3, 5, 0)
        Case "Neurológica"
            Call CBPreenche(5, Sheets("Geral"), 3, 4, 0)
    End Select
End Sub

Private Sub CB_Lesões_Change()
    If CB_Lesões.Value = "Óssea" Then
        CB_OrigemLesão.Enabled = True
    Else
        CB_OrigemLesão.Enabled = False
        CB_SRED.Enabled = False
    End If
End Sub

Private Sub CB_OrigemLesão_Change()
    If CB_OrigemLesão.Value = "Por Estresse" Then
        CB_SRED.Enabled = True
    Else
        CB_SRED.Enabled = False
    End If
End Sub

Private Sub CB_ParteCorpo_AfterUpdate()
    Dim coluna As Integer
    
    Select Case UF_CadetesLesões.CB_Lesões.Value
        Case "Óssea"
            Select Case UF_CadetesLesões.CB_ParteCorpo.Value
                Case "Membros Superiores"
                    Call CBPreenche(3, Sheets("Óssea"), 1, 7, 1)
                Case "Coluna"
                    Call CBPreenche(3, Sheets("Óssea"), 8, 11, 1)
                Case "Bacia"
                    Call CBPreenche(3, Sheets("Óssea"), 12, 12, 1)
                Case "Membros Inferiores"
                    Call CBPreenche(3, Sheets("Óssea"), 13, 19, 1)
            End Select
        Case "Articular"
            Select Case UF_CadetesLesões.CB_ParteCorpo.Value
                Case "Membros Superiores"
                    Call CBPreenche(3, Sheets("Articular"), 1, 6, 1)
                 Case "Coluna"
                    Call CBPreenche(3, Sheets("Articular"), 7, 10, 1)
                Case "Bacia"
                    Call CBPreenche(3, Sheets("Articular"), 11, 11, 1)
                Case "Membros Inferiores"
                    Call CBPreenche(3, Sheets("Articular"), 12, 16, 1)
            End Select
        Case "Muscular"
            Select Case UF_CadetesLesões.CB_ParteCorpo.Value
                Case "Membros Superiores"
                    Call CBPreenche(3, Sheets("Muscular"), 1, 3, 1)
                Case "Coluna"
                    Call CBPreenche(3, Sheets("Muscular"), 4, 4, 1)
                Case "Tórax"
                    Call CBPreenche(3, Sheets("Muscular"), 5, 5, 1)
                Case "Core"
                    Call CBPreenche(3, Sheets("Muscular"), 6, 7, 1)
                Case "Membros Inferiores"
                    Call CBPreenche(3, Sheets("Muscular"), 8, 10, 1)
            End Select
        Case "Tendinosa"
            Select Case UF_CadetesLesões.CB_ParteCorpo.Value
                Case "Membros Superiores"
                    Call CBPreenche(3, Sheets("Tendinosa"), 1, 3, 1)
                 Case "Bacia"
                    Call CBPreenche(3, Sheets("Tendinosa"), 4, 4, 1)
                Case "Membros Inferiores"
                    Call CBPreenche(3, Sheets("Tendinosa"), 5, 8, 1)
            End Select
        Case "Neurológica"
            Select Case UF_CadetesLesões.CB_ParteCorpo.Value
                Case "Membros Superiores"
                    Call CBPreenche(3, Sheets("Neurológica"), 1, 1, 1)
                Case "Membros Inferiores"
                    Call CBPreenche(3, Sheets("Neurológica"), 2, 2, 1)
            End Select
    End Select
End Sub

Private Sub CB_ParteLesionada_AfterUpdate()
    Dim linha As Integer
    
    Select Case UF_CadetesLesões.CB_Lesões.Value
        Case "Óssea"
            Select Case UF_CadetesLesões.CB_ParteCorpo.Value
                Case "Membros Superiores"
                    Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                        Case "Ombro"
                            Call CBPreenche(1, Sheets("Óssea"), 4, 6, 2)
                        Case "Braço"
                            Call CBPreenche(2, Sheets("Óssea"), 4, 4, 2)
                        Case "Cotovelo"
                            Call CBPreenche(3, Sheets("Óssea"), 4, 7, 2)
                        Case "Antebraço"
                            Call CBPreenche(4, Sheets("Óssea"), 4, 5, 2)
                        Case "Punho"
                            Call CBPreenche(5, Sheets("Óssea"), 4, 13, 2)
                        Case "Mão"
                            Call CBPreenche(6, Sheets("Óssea"), 4, 8, 2)
                        Case "Mão - dedos"
                            Call CBPreenche(7, Sheets("Óssea"), 4, 17, 2)
                    End Select
                Case "Coluna"
                    Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                        Case "Cervical"
                            Call CBPreenche(8, Sheets("Óssea"), 4, 10, 2)
                        Case "Torácica"
                            Call CBPreenche(9, Sheets("Óssea"), 4, 15, 2)
                        Case "Lombar"
                            Call CBPreenche(10, Sheets("Óssea"), 4, 8, 2)
                        Case "Sacrococcígea"
                            Call CBPreenche(11, Sheets("Óssea"), 4, 9, 2)
                    End Select
                Case "Bacia"
                    Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                        Case "Bacia"
                            Call CBPreenche(12, Sheets("Óssea"), 4, 6, 2)
                    End Select
                Case "Membros Inferiores"
                    Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                        Case "Quadril"
                            Call CBPreenche(13, Sheets("Óssea"), 4, 5, 2)
                        Case "Coxa"
                            Call CBPreenche(14, Sheets("Óssea"), 4, 4, 2)
                        Case "Joelho"
                            Call CBPreenche(15, Sheets("Óssea"), 4, 5, 2)
                        Case "Perna"
                            Call CBPreenche(16, Sheets("Óssea"), 4, 6, 2)
                        Case "Tornozelo"
                            Call CBPreenche(17, Sheets("Óssea"), 4, 9, 2)
                        Case "Pé"
                            Call CBPreenche(18, Sheets("Óssea"), 4, 14, 2)
                        Case "Pé - dedos"
                            Call CBPreenche(19, Sheets("Óssea"), 4, 17, 2)
                    End Select
            End Select
        Case "Articular"
            Select Case UF_CadetesLesões.CB_ParteCorpo.Value
                Case "Membros Superiores"
                    Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                        Case "Esternoclavicular"
                            Call CBPreenche(1, Sheets("Articular"), 4, 4, 2)
                        Case "Ombro"
                            Call CBPreenche(2, Sheets("Articular"), 4, 12, 2)
                        Case "Cotovelo"
                            Call CBPreenche(3, Sheets("Articular"), 4, 8, 2)
                        Case "Punho"
                            Call CBPreenche(4, Sheets("Articular"), 4, 12, 2)
                        Case "Mão"
                            Call CBPreenche(5, Sheets("Articular"), 4, 9, 2)
                        Case "Dedos"
                            Call CBPreenche(6, Sheets("Articular"), 4, 23, 2)
                    End Select
                Case "Coluna"
                    Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                        Case "Cervical"
                            Call CBPreenche(7, Sheets("Articular"), 4, 18, 2)
                        Case "Torácica"
                            Call CBPreenche(8, Sheets("Articular"), 4, 26, 2)
                        Case "Lombar"
                            Call CBPreenche(9, Sheets("Articular"), 4, 14, 2)
                        Case "Sacrococcígea"
                            Call CBPreenche(10, Sheets("Articular"), 4, 6, 2)
                    End Select
                Case "Bacia"
                    Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                        Case "Bacia"
                            Call CBPreenche(11, Sheets("Articular"), 4, 8, 2)
                    End Select
                Case "Membros Inferiores"
                    Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                        Case "Quadril"
                            Call CBPreenche(12, Sheets("Articular"), 4, 8, 2)
                        Case "Joelho"
                            Call CBPreenche(13, Sheets("Articular"), 4, 16, 2)
                        Case "Tornozelo"
                            Call CBPreenche(14, Sheets("Articular"), 4, 8, 2)
                        Case "Pé"
                            Call CBPreenche(15, Sheets("Articular"), 4, 11, 2)
                        Case "Dedos"
                            Call CBPreenche(16, Sheets("Articular"), 4, 22, 2)
                    End Select
            End Select
        Case "Muscular"
            Select Case UF_CadetesLesões.CB_ParteCorpo.Value
                Case "Membros Superiores"
                    Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                        Case "Ombro"
                            Call CBPreenche(1, Sheets("Muscular"), 4, 8, 2)
                        Case "Braço"
                            Call CBPreenche(2, Sheets("Muscular"), 4, 7, 2)
                        Case "Antebraço"
                            Call CBPreenche(3, Sheets("Muscular"), 4, 6, 2)
                    End Select
                Case "Coluna"
                    Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                        Case "Cervical"
                            Call CBPreenche(4, Sheets("Muscular"), 4, 5, 2)
                    End Select
                Case "Tórax"
                    Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                        Case "Caixa torácica"
                            Call CBPreenche(5, Sheets("Muscular"), 4, 7, 2)
                    End Select
                Case "Core"
                    Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                        Case "Lombar"
                            Call CBPreenche(6, Sheets("Muscular"), 4, 5, 2)
                        Case "Abdome"
                            Call CBPreenche(7, Sheets("Muscular"), 4, 4, 2)
                    End Select
                Case "Membros Inferiores"
                    Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                        Case "Quadril"
                            Call CBPreenche(8, Sheets("Muscular"), 4, 8, 2)
                        Case "Coxa"
                            Call CBPreenche(9, Sheets("Muscular"), 4, 9, 2)
                        Case "Perna"
                            Call CBPreenche(10, Sheets("Muscular"), 4, 10, 2)
                    End Select
            End Select
            Case "Tendinosa"
                Select Case UF_CadetesLesões.CB_ParteCorpo.Value
                    Case "Membros Superiores"
                        Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                            Case "Ombro"
                                Call CBPreenche(1, Sheets("Tendinosa"), 4, 11, 2)
                            Case "Cotovelo"
                                Call CBPreenche(2, Sheets("Tendinosa"), 4, 7, 2)
                            Case "Punho"
                                Call CBPreenche(3, Sheets("Tendinosa"), 4, 8, 2)
                        End Select
                    Case "Bacia"
                        Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                            Case "Bacia"
                                Call CBPreenche(4, Sheets("Tendinosa"), 4, 7, 2)
                        End Select
                    Case "Membros Inferiores"
                        Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                            Case "Quadril"
                                Call CBPreenche(5, Sheets("Tendinosa"), 4, 7, 2)
                            Case "Joelho"
                                Call CBPreenche(6, Sheets("Tendinosa"), 4, 11, 2)
                            Case "Tornozelo"
                                Call CBPreenche(7, Sheets("Tendinosa"), 4, 7, 2)
                            Case "Pé"
                                Call CBPreenche(8, Sheets("Tendinosa"), 4, 5, 2)
                        End Select
            End Select
            Case "Neurológica"
                Select Case UF_CadetesLesões.CB_ParteCorpo.Value
                    Case "Membros Superiores"
                        Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                            Case "Plexo braquial"
                                Call CBPreenche(1, Sheets("Neurológica"), 4, 11, 2)
                        End Select
                    Case "Membros Inferiores"
                        Select Case UF_CadetesLesões.CB_ParteLesionada.Value
                            Case "Plexo lombossacro"
                                Call CBPreenche(2, Sheets("Neurológica"), 4, 7, 2)
                        End Select
            End Select
    End Select
End Sub

Private Sub B_Salvar_Click()
    Dim linha As Integer
    Dim c As Control
    Dim objeto As String
    Dim nome As String
    
If UF_CadetesLesões.CB_Médico.Value = "" Then
    MsgBox "Não esqueça de informar o Médico!!!"
Else
    If Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(1, 1).Value <> " " Then
        linha = Worksheets("BD_Atendimento").Range("Tab_Atendimento").Rows.Count + 1
    Else
        linha = Worksheets("BD_Atendimento").Range("Tab_Atendimento").Rows.Count
    End If
    
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 1).Value = UF_CadetesLesões.TB_NúmeroCad.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 2).Value = UF_CadetesLesões.TB_Data.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 3).Value = UF_CadetesLesões.TB_Hora.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 4).Value = UF_CadetesLesões.TB_AnoCad.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 5).Value = UF_CadetesLesões.TB_CursoCad.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 6).Value = UF_CadetesLesões.TB_Subunidade.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 7).Value = UF_CadetesLesões.TB_Pelotão.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 8).Value = UF_CadetesLesões.TB_CmtCurso.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 9).Value = UF_CadetesLesões.TB_CmtSubunidade.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 10).Value = UF_CadetesLesões.TB_CmtPelotão.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 11).Value = UF_CadetesLesões.L_Profissional.Caption
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 12).Value = UF_CadetesLesões.CB_Médico.Value
    If UF_CadetesLesões.B_Inicial.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 13).Value = "Inicial"
    Else
        If UF_CadetesLesões.B_Retorno.Value = "Verdadeiro" Then
            Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 13).Value = "Retorno"
        End If
    End If
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 14).Value = UF_CadetesLesões.CB_Lesões.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 15).Value = UF_CadetesLesões.CB_ParteCorpo.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 16).Value = UF_CadetesLesões.CB_Lateralidade.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 17).Value = UF_CadetesLesões.CB_ParteLesionada.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 18).Value = UF_CadetesLesões.CB_LocalLesão.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 19).Value = UF_CadetesLesões.CB_OrigemLesão.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 20).Value = UF_CadetesLesões.CB_SRED.Value
    If UF_CadetesLesões.B_Preventiva.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 21).Value = "Preventiva"
    Else
        If UF_CadetesLesões.B_DecAtiv.Value = "Verdadeiro" Then
            Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 21).Value = "Decorrente da Atividade"
        End If
    End If
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 22).Value = UF_CadetesLesões.CB_Atividade.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 23).Value = UF_CadetesLesões.CB_TFMTAF.Value
    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 24).Value = UF_CadetesLesões.CB_Modalidade.Value
    If UF_CadetesLesões.B_Cirúrgico.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 25).Value = "Cirúrgico"
    Else
        If UF_CadetesLesões.B_Conservador.Value = "Verdadeiro" Then
            Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 25).Value = "Conservador"
        Else
            If UF_CadetesLesões.B_PósOperatório.Value = "Verdadeiro" Then
                Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 25).Value = "PósOperatório"
            Else
                If UF_CadetesLesões.B_AguardaExame.Value = "Verdadeiro" Then
                    Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 25).Value = "Aguardar Exame"
                End If
            End If
        End If
    End If
    If UF_CadetesLesões.C_Sim.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 26).Value = "Sim"
    Else
        If UF_CadetesLesões.C_Não.Value = "Verdadeiro" Then
            Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 26).Value = "Não"
        End If
    End If
    If UF_CadetesLesões.C_Fisioterapia.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 27).Value = "X"
    End If
    If UF_CadetesLesões.C_SEF.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 28).Value = "X"
    End If
    If UF_CadetesLesões.C_Nutricionista.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 29).Value = "X"
    End If
    If UF_CadetesLesões.C_Psicopedagógica.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 30).Value = "X"
    End If
    If UF_CadetesLesões.C_RX.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 31).Value = "X"
    End If
    If UF_CadetesLesões.C_USG.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 32).Value = "X"
    End If
    If UF_CadetesLesões.C_TC.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 33).Value = "X"
    End If
    If UF_CadetesLesões.C_RM.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 34).Value = "X"
    End If
    If UF_CadetesLesões.C_DEXA.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 35).Value = "X"
    End If
    If UF_CadetesLesões.C_ExameSangue.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 36).Value = "X"
    End If
    If UF_CadetesLesões.C_Dispensa.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 37).Value = "X"
    End If
    If UF_CadetesLesões.C_VCL.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 38).Value = "X"
    End If
    If UF_CadetesLesões.C_Alta.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 39).Value = "X"
    End If
    If UF_CadetesLesões.C_RiscoCirúrgico.Value = "Verdadeiro" Then
        Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(linha, 40).Value = "X"
    End If
    'Limpa os campos do User Form para novo preenchimento
    For Each c In Controls
        nome = c.Name
        objeto = VBA.TypeName(c)
        If objeto = "TextBox" Or objeto = "ComboBox" Then
            If nome <> "TB_NúmeroCad" Then
                If nome <> "TB_Data" Then
                    If nome <> "TB_Hora" Then
                        UF_CadetesLesões.Controls(nome) = Clear
                    End If
                End If
            End If
        End If
    Next
End If
End Sub

Private Sub TB_Data_Change()

End Sub

Private Sub TB_NúmeroCad_AfterUpdate()
    Dim num As Integer
    
    For Each c In Controls
        nome = c.Name
        objeto = VBA.TypeName(c)
        If objeto = "TextBox" Or objeto = "ComboBox" Then
            If nome <> "TB_NúmeroCad" Then
                        UF_CadetesLesões.Controls(nome) = Clear
            End If
        End If
        If objeto = "OptionButton" Or objeto = "CheckBox" Then
            UF_CadetesLesões.Controls(nome) = False
        End If
    Next
    
    UF_CadetesLesões.TB_Data.Value = VBA.Date
    UF_CadetesLesões.TB_Hora.Value = Time
    
    num = UF_CadetesLesões.TB_NúmeroCad.Value
    Call BuscaCadete(num)
    UF_CadetesLesões.TB_NomeCad.Enabled = False
    UF_CadetesLesões.TB_GuerraCad.Enabled = False
    UF_CadetesLesões.TB_AnoCad.Enabled = False
    UF_CadetesLesões.TB_CursoCad.Enabled = False
    UF_CadetesLesões.TB_Subunidade.Enabled = False
    UF_CadetesLesões.TB_Pelotão.Enabled = False
    UF_CadetesLesões.TB_CmtCurso.Enabled = False
    UF_CadetesLesões.TB_CmtSubunidade.Enabled = False
    UF_CadetesLesões.TB_CmtPelotão.Enabled = False
    
    'If UF_CadetesLesões.TB_NúmeroCad.Value <> "" Then
    '    Call RecuperaDados(UF_CadetesLesões.TB_NúmeroCad.Value)
    'End If

    
End Sub

'Private Sub TB_NúmeroCad_Change()
'    If UF_CadetesLesões.TB_NúmeroCad.Value <> "" Then
'        Call RecuperaDados(UF_CadetesLesões.TB_NúmeroCad.Value)
'    End If
'End Sub

Private Sub UserForm_Initialize()
    Dim linha As Integer
    Dim totlinhas As Integer
    
    For linha = 3 To 7
        CB_Lesões.AddItem Sheets("Geral").Cells(linha, 1)
    Next linha
    
    For linha = 3 To 5
        CB_Lateralidade.AddItem Sheets("Geral").Cells(linha, 10)
    Next linha
    
    totlinhas = Worksheets("Atividade").Range("Tab_Atividade").Rows.Count
    For linha = 1 To totlinhas
        CB_Atividade.AddItem Worksheets("Atividade").Range("Tab_Atividade").Cells(linha, 1)
    Next linha
    
    totlinhas = Worksheets("Atividade").Range("Tab_TFMTAF").Rows.Count
    For linha = 1 To totlinhas
        CB_TFMTAF.AddItem Worksheets("Atividade").Range("Tab_TFMTAF").Cells(linha, 1)
    Next linha

    totlinhas = Worksheets("Atividade").Range("Tab_Modalidade").Rows.Count
    For linha = 1 To totlinhas
      CB_Modalidade.AddItem Worksheets("Atividade").Range("Tab_Modalidade").Cells(linha, 1)
    Next linha
    
    totlinhas = Worksheets("Atividade").Range("Tab_OrigemLesão").Rows.Count
    For linha = 1 To totlinhas
        CB_OrigemLesão.AddItem Worksheets("Atividade").Range("Tab_OrigemLesão").Cells(linha, 1)
        CB_OrigemLesão.Enabled = False
    Next linha
    
    totlinhas = Worksheets("Atividade").Range("Tab_SRED").Rows.Count
    For linha = 1 To totlinhas
        CB_SRED.AddItem Worksheets("Atividade").Range("Tab_SRED").Cells(linha, 1)
        CB_SRED.Enabled = False
    Next linha
    
    totlinhas = Worksheets("BD_Profissionais").Range("Tab_Médico").Rows.Count
    For linha = 1 To totlinhas
        CB_Médico.AddItem Worksheets("BD_Profissionais").Range("Tab_Médico").Cells(linha, 1)
    Next linha
                
    UF_CadetesLesões.F_Lesão.Enabled = False
    UF_CadetesLesões.TB_Data.Value = VBA.Date
    UF_CadetesLesões.TB_Hora.Value = Time

End Sub

Sub BuscaCadete(número As Integer)
    Dim totlinhas As Integer
    Dim cont As Integer
    Dim flag As Integer
    
    totlinhas = Worksheets("BD_Cadetes").Range("Tab_Cadetes").Rows.Count
    flag = 0
    
    For cont = 1 To totlinhas
        If Worksheets("BD_Cadetes").Range("Tab_Cadetes").Cells(cont, 1) = número Then
            UF_CadetesLesões.TB_NomeCad.Value = Worksheets("BD_Cadetes").Range("Tab_Cadetes").Cells(cont, 2).Value
            UF_CadetesLesões.TB_GuerraCad.Value = Worksheets("BD_Cadetes").Range("Tab_Cadetes").Cells(cont, 3)
            UF_CadetesLesões.TB_CursoCad.Value = Worksheets("BD_Cadetes").Range("Tab_Cadetes").Cells(cont, 4)
            UF_CadetesLesões.TB_AnoCad.Value = Worksheets("BD_Cadetes").Range("Tab_Cadetes").Cells(cont, 5)
            UF_CadetesLesões.TB_Subunidade.Value = Worksheets("BD_Cadetes").Range("Tab_Cadetes").Cells(cont, 6).Value
            UF_CadetesLesões.TB_Pelotão.Value = Worksheets("BD_Cadetes").Range("Tab_Cadetes").Cells(cont, 7)
            UF_CadetesLesões.TB_CmtCurso.Value = Worksheets("BD_Cadetes").Range("Tab_Cadetes").Cells(cont, 8)
            UF_CadetesLesões.TB_CmtSubunidade.Value = Worksheets("BD_Cadetes").Range("Tab_Cadetes").Cells(cont, 9)
            UF_CadetesLesões.TB_CmtPelotão.Value = Worksheets("BD_Cadetes").Range("Tab_Cadetes").Cells(cont, 10)
            cont = totlinhas
            flag = 1
        End If
    Next
    
    If flag = 0 Then
        MsgBox "Cadete inexistente ..."
    End If
    
End Sub

Sub CBPreenche(x As Integer, nome As Worksheet, início As Integer, fim As Integer, flag As Integer)
    Dim y As Integer
    
    Select Case flag
        Case 0
            UF_CadetesLesões.CB_ParteCorpo.Clear
            UF_CadetesLesões.CB_ParteLesionada.Clear
            UF_CadetesLesões.CB_LocalLesão.Clear
            For y = início To fim
                UF_CadetesLesões.CB_ParteCorpo.AddItem nome.Cells(y, x)
            Next
            
        Case 1
            UF_CadetesLesões.CB_ParteLesionada.Clear
            UF_CadetesLesões.CB_LocalLesão.Clear
            For y = início To fim
                UF_CadetesLesões.CB_ParteLesionada.AddItem nome.Cells(x, y)
            Next
            
        Case 2
            UF_CadetesLesões.CB_LocalLesão.Clear
            For y = início To fim
                UF_CadetesLesões.CB_LocalLesão.AddItem nome.Cells(y, x)
            Next
    End Select
End Sub

Sub DadosRetorno()
    Dim totlinhas As Integer
    Dim cont As Integer
    Dim linha As Integer
    
    totlinhas = Worksheets("BD_Atendimento").Range("Tab_Atendimento").Rows.Count
    For cont = 1 To totlinhas
        If Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(cont, 1).Value = CInt(UF_CadetesLesões.TB_NúmeroCad.Value) And Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(cont, 2).Value = CDate(UF_CadetesLesões.CB_DataRet.Value) And FormatDateTime(Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(cont, 3).Value) = UF_CadetesLesões.CB_HoraRet.Value Then
            linha = cont
            cont = totlinhas
        End If
    Next
    Call RecuperaRetorno(linha)
End Sub

Sub DadosRetorno()
    Dim totlinhas As Integer
    Dim cont As Integer
    Dim linha As Integer
    
    totlinhas = Worksheets("BD_Atendimento").Range("Tab_Atendimento").Rows.Count
    For cont = 1 To totlinhas
        If Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(cont, 1).Value = CInt(UF_CadetesLesões.TB_NúmeroCad.Value) And Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(cont, 2).Value = CDate(UF_CadetesLesões.CB_DataRet.Value) And FormatDateTime(Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(cont, 3).Value) = UF_CadetesLesões.CB_HoraRet.Value Then
            linha = cont
            cont = totlinhas
        End If
    Next
    Call RecuperaRetorno(linha)
End Sub

Sub DadosRetorno()
    Dim totlinhas As Integer
    Dim cont As Integer
    Dim linha As Integer
    
    totlinhas = Worksheets("BD_Atendimento").Range("Tab_Atendimento").Rows.Count
    For cont = 1 To totlinhas
        If Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(cont, 1).Value = CInt(UF_CadetesLesões.TB_NúmeroCad.Value) And Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(cont, 2).Value = CDate(UF_CadetesLesões.CB_DataRet.Value) And FormatDateTime(Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(cont, 3).Value) = UF_CadetesLesões.CB_HoraRet.Value Then
            linha = cont
            cont = totlinhas
        End If
    Next
    Call RecuperaRetorno(linha)
End Sub

Sub DadosRetorno()
    Dim totlinhas As Integer
    Dim cont As Integer
    Dim linha As Integer
    
    totlinhas = Worksheets("BD_Atendimento").Range("Tab_Atendimento").Rows.Count
    For cont = 1 To totlinhas
        If Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(cont, 1).Value = CInt(UF_CadetesLesões.TB_NúmeroCad.Value) And Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(cont, 2).Value = CDate(UF_CadetesLesões.CB_DataRet.Value) And FormatDateTime(Worksheets("BD_Atendimento").Range("Tab_Atendimento").Cells(cont, 3).Value) = UF_CadetesLesões.CB_HoraRet.Value Then
            linha = cont
            cont = totlinhas
        End If
    Next
    Call RecuperaRetorno(linha)
End Sub

For linha = 1 To totlinhas
        CB_OrigemLesão.AddItem Worksheets("Atividade").Range("Tab_OrigemLesão").Cells(linha, 1)
        CB_OrigemLesão.Enabled = False
    Next linha
    
    totlinhas = Worksheets("Atividade").Range("Tab_SRED").Rows.Count
    For linha = 1 To totlinhas
        CB_SRED.AddItem Worksheets("Atividade").Range("Tab_SRED").Cells(linha, 1)
        CB_SRED.Enabled = False
    Next linha
    
    totlinhas = Worksheets("BD_Profissionais").Range("Tab_Médico").Rows.Count
    For linha = 1 To totlinhas
        CB_Médico.AddItem Worksheets("BD_Profissionais").Range("Tab_Médico").Cells(linha, 1)
    Next linha
                
    UF_CadetesLesões.F_Lesão.Enabled = False
    UF_CadetesLesões.TB_Data.Value = VBA.Date
    UF_CadetesLesões.TB_Hora.Value = Time

End Sub
